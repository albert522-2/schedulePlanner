from cmu_graphics import *
import math #for sortingAlgo when rounding, also for checking bugs

"""
#backend stuff
"""

class Task:

    def __init__(self, name, description, weight, cost, deadline):
        self.name = name
        self.description = description
        self.weight = weight
        self.cost = cost
        self.deadline = deadline

    def weightCostRatio(self):
        return self.weight / self.cost

    def __repr__(self):
        return f'{self.name}: cost={self.cost}, weight={self.weight}, deadline={self.deadline}'


def insertedWeight(tasks, insertIndex):
    if not tasks:
        return 10.0
    
    if insertIndex <= 0:
        return tasks[0].weight + 1.0
    
    if insertIndex >= len(tasks):
        return tasks[-1].weight / 2
    
    return (tasks[insertIndex - 1].weight + tasks[insertIndex].weight) / 2
        #note insertIndex used here as that value gets moved to the "top"


def sortingAlgo(tasks, availHours):
    chosen, dropped = [], []
    for task in sorted(tasks, key=lambda task: task.deadline): #uses deadline to compare
        chosen.append(task)
        total = sum(task.cost for task in chosen)
        limit = min(task.deadline, availHours)

        #ignore tiny rounding differences when adding decimal hours
        while chosen and total > limit and not math.isclose(total, limit, rel_tol=1e-12, abs_tol=0):
            lowest = min(chosen, key=lambda task: task.weightCostRatio())
            chosen.remove(lowest)
            dropped.append(lowest)
            total = sum(task.cost for task in chosen) #drops lowest priority task

    #checking if deferred tasks can be added if other tasks were removed
    for task in sorted(dropped, key=lambda task: task.weightCostRatio(), reverse=True):
        trial = sorted(chosen + [task], key=lambda task: task.deadline)
        total = 0
        fits = True

        for scheduledTask in trial:
            total += scheduledTask.cost
            limit = min(scheduledTask.deadline, availHours)

            if total > limit and not math.isclose(total, limit, rel_tol=1e-12, abs_tol=0):
                fits = False
                break

        if fits:
            chosen = trial
            dropped.remove(task)

    return chosen, dropped


def addTask(tasks, name, description, cost, deadline, insertIndex):
    insertIndex = max(0, min(insertIndex, len(tasks)))
    task = Task(name, description, insertedWeight(tasks, insertIndex), cost, deadline)
    tasks.insert(insertIndex, task)


def runScheduler(tasks, availableHours):
    return sortingAlgo(tasks, availableHours)

"""
model for storing application data
"""

def onAppStart(app):
    app.background = rgb(246, 248, 252)
    app.tasks = [] #tasks list
    app.availableHours = 8.0
    app.page = 0
    app.mouseX, app.mouseY = -1, -1
    app.message = 'Add a task to start planning.'
    app.buttons = {'Add task': (24, 130, 220, 42),
                   'Set available hours': (24, 186, 220, 42),
                   'Previous': (app.width - 220, 718, 88, 34),
                   'Next': (app.width - 120, 718, 88, 34)}
    refreshSchedule(app)


def refreshSchedule(app):
    app.chosen, app.dropped = runScheduler(app.tasks, app.availableHours)
    app.displayTasks = app.chosen + app.dropped
    app.page = min(app.page, max(0, (len(app.displayTasks) - 1) // 5)) #5 is the number of tasks allowed on one page


def contains(box, x, y): #checks if (x,y) is in box
    left, top, width, height = box
    return left <= x <= left + width and top <= y <= top + height


def deleteBox(app, row): #the 'X' delete button for a specific row (task)
    return (app.width - 68, 150 + row * 110 + 8, 28, 26)

"""
controller: collect inputs and change tasks
also refresh the model here
"""

def inputTask(app):
    values = []
    prompts = ['Task name:', 'Description (optional):', 'Duration in hours:',
               'Deadline in whole hours from now:',
               f'Priority position (1 to {len(app.tasks) + 1}; 1 is highest):']
    
    for prompt in prompts:
        value = app.getTextInput(prompt) #creates new screens for inputs
        if value is None:
            return #i.e. don't create a task
        
        values.append(value.strip())

    try: #checking for various errors
        name, description = values[:2]
        cost, deadline, position = float(values[2]), int(values[3]), int(values[4])

        if not name or not math.isfinite(cost) or cost <= 0 or deadline < 0 or not math.isfinite(deadline):
            raise ValueError
        
        if not 1 <= position <= len(app.tasks) + 1:
            raise ValueError
        
        weight = insertedWeight(app.tasks, position - 1)

        if not math.isfinite(weight / cost) or weight <= 0:
            raise ValueError
        
    except (ValueError, OverflowError):
        app.message = 'Check the name, positive duration, deadline, and priority.'
        return
    
    addTask(app.tasks, name, description, cost, deadline, position - 1)
    app.page = 0
    refreshSchedule(app)
    app.message = f'Added {name}.'


def inputHours(app):
    value = app.getTextInput('Available hours from now (zero or greater):')
    if value is None:
        return
    
    try:
        hours = float(value)
        if not math.isfinite(hours) or hours < 0:
            raise ValueError
        
    except ValueError:
        app.message = 'Enter a finite number of hours, zero or greater.'
        return
    
    app.availableHours = hours
    app.page = 0
    refreshSchedule(app)
    app.message = 'Schedule updated.'


def changePage(app, step):
    lastPage = max(0, (len(app.displayTasks) - 1) // 5)
    app.page = max(0, min(lastPage, app.page + step))

#tracks mouse position, clicks
def onMouseMove(app, mouseX, mouseY):
    app.mouseX, app.mouseY = mouseX, mouseY


def onMouseDrag(app, mouseX, mouseY): 
    app.mouseX, app.mouseY = mouseX, mouseY

#click buttons
def onMousePress(app, mouseX, mouseY):
    app.mouseX, app.mouseY = mouseX, mouseY

    for row, task in enumerate(app.displayTasks[app.page * 5:app.page * 5 + 5]): #extracts the 5 tasks from each page
        if contains(deleteBox(app, row), mouseX, mouseY): #if the delete button is clicked
            app.tasks.remove(task)
            refreshSchedule(app)
            app.message = f'Deleted {task.name}.'
            return
        
    for name, box in app.buttons.items():
        if contains(box, mouseX, mouseY):
            if name == 'Add task':
                inputTask(app)

            elif name == 'Set available hours':
                inputHours(app)

            else:
                changePage(app, -1 if name == 'Previous' else 1)

            return


def onKeyPress(app, key):
    if key in ('left', 'right'):
        changePage(app, -1 if key == 'left' else 1)

"""
view: actual graphics stuff
DO NOT MODIFY ANY FUNCTIONS/VARS IN PREVIOUS PARTS HERE
"""

def label(text, x, y, size=14, color='black', bold=False):
    drawLabel(text, x, y, align='left', font='arial', size=size, fill=color, bold=bold)


def drawButton(app, text, box, enabled=True):
    x, y, width, height = box
    color = rgb(236, 240, 248)

    if enabled and contains(box, app.mouseX, app.mouseY):
        color = rgb(215, 224, 238) #darkens the color

    drawRect(x, y, width, height, fill=color)
    drawLabel(text, x + width / 2, y + height / 2, font='arial', size=14,
              fill='black' if enabled else 'gray')


def urgencyColor(deadline):
    if deadline <= 2:
        return rgb(195, 65, 65) #red
    
    if deadline <= 6:
        return rgb(190, 145, 30) #yellow
    
    return rgb(45, 139, 85) #green


def drawTask(app, task, row, index):
    x, y, width = 280, 150 + row * 110, app.width - 304
    color = urgencyColor(task.deadline)
    drawRect(x, y, width, 100, fill='white', border=rgb(224, 230, 240))
    drawRect(x, y, 5, 100, fill=color)
    label(task.name[:26], x + 16, y + 20, size=17, bold=True)

    if task in app.chosen:
        start = sum(task.cost for task in app.chosen[:index])
        status = f'{start:g}-{start + task.cost:g}h from now'

    else:
        status = 'Deferred'

    label(status, app.width - 242, y + 20, size=13, color=color)
    drawButton(app, 'X', deleteBox(app, row))

    #shorten long text so the card stays readable
    label(task.description[:50], x + 16, y + 46, size=13, color='dimGray')
    details = (f'Priority #{app.tasks.index(task) + 1}   Duration: {task.cost:g}h'
               f'   Due: {task.deadline:g}h   Weight: {task.weight:g}')
    label(details, x + 16, y + 76, size=13)


def redrawAll(app):
    drawRect(0, 0, app.width, 90, fill='white')
    label('Task Scheduler', 24, 40, size=28, bold=True)
    label('Plan your time', 24, 70, size=14, color='dimGray')
    label(f'Available: {app.availableHours:g} hours', 24, 110, bold=True)

    for name, box in app.buttons.items():
        enabled = True

        if name == 'Previous':
            enabled = app.page > 0

        elif name == 'Next':
            enabled = (app.page + 1) * 5 < len(app.displayTasks)

        drawButton(app, name, box, enabled)
    label('Deadline urgency', 24, 282, bold=True)

    for row, (text, hours) in enumerate([('Red: within 2h', 2), ('Yellow: 3-6h', 6),
                                        ('Green: over 6h', 7)]):
        label(text, 24, 312 + row * 28, color=urgencyColor(hours))

    label('Click X to delete a task.', 24, 420, size=13)
    label('Arrow keys change pages.', 24, 448, size=13)
    total = sum(task.cost for task in app.chosen)

    label(f'{total:g}h planned | {len(app.chosen)} scheduled | {len(app.dropped)} deferred',
          280, 120, bold=True)
    
    for row, task in enumerate(app.displayTasks[app.page * 5:app.page * 5 + 5]):
        drawTask(app, task, row, app.page * 5 + row)

    if not app.displayTasks:
        label('No tasks yet. Click Add task.', 280, 190, size=20)

    label(f'Page {app.page + 1}', 280, 736)
    label(app.message[:110], 24, 775, size=13, color='dimGray')


if __name__ == '__main__':
    runApp(width=1000, height=800)


""" Testing testing (from Gemini)
For the backend only

if __name__ == "__main__":
    # Test Setup:
    # 1. Respond to Emails:     Cost 1.0h, Deadline 2h, Weight 5.0 (Ratio: 5.00)
    # 2. Read Chapter 3:        Cost 3.0h, Deadline 4h, Weight 2.0 (Ratio: 0.67) -> Lowest ratio, dropped first when time overflows.
    # 3. 15-112 Homework:       Cost 4.0h, Deadline 5h, Weight 10.0 (Ratio: 2.50) -> Long cost, pushes currTime past deadline (2+3+4=9 > 5), causing t2 drop, then itself drops.
    # 4. Review Lecture Notes:  Cost 2.0h, Deadline 6h, Weight 8.0 (Ratio: 4.00) -> Fits safely after low-ratio tasks are dropped.

    t1 = Task("15-112 Homework", "Coding assignment", weight=10.0, cost=4.0, deadline=5)
    t2 = Task("Read Chapter 3", "Textbook reading", weight=2.0, cost=3.0, deadline=4)
    t3 = Task("Respond to Emails", "Quick replies", weight=5.0, cost=1.0, deadline=2)
    t4 = Task("Review Lecture Notes", "Exam prep", weight=8.0, cost=2.0, deadline=6)

    sample_tasks = [t1, t2, t3, t4]
    
    # Run with availHours = 8 (or 24)
    chosen, dropped = sortingAlgo(sample_tasks, availHours=8)
    
    print("--- SCHEDULED TASKS ---")
    for t in chosen:
        print(f"{t.name} (Cost: {t.cost}h, Weight: {t.weight}, Ratio: {t.weightCostRatio():.2f}, Deadline: {t.deadline}h)")
        
    print("\n--- DROPPED TASKS ---")
    for t in dropped:
        print(f"{t.name} (Cost: {t.cost}h, Weight: {t.weight}, Ratio: {t.weightCostRatio():.2f}, Deadline: {t.deadline}h)")


"""
