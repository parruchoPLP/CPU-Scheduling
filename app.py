from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)

class algo_util:
    def get_total_burst(self, task_list):
        total_burst = 0
        for task in task_list:
            total_burst += task.cpu_burst
        return total_burst

    def task_waiting_time(self, time_executed, arrival_time):
        return time_executed - arrival_time

    def task_turnaround_time(self, time_of_completion, arrival_time):
        return time_of_completion - arrival_time

    def avg(self, lst):
        num = 0
        for i in lst:
            num += i
        result = num / len(lst) if lst else 0
        return round(result, 4)


class Task:
    tasks = []

    def __init__(self, id: str, arrival_time: int, cpu_burst: int) -> None:
        if len(id) != 1:
            raise ValueError("Task ID must be a single character.")
        if self.check_id_exists(id):
            raise ValueError("Task ID must be unique.")
        self.id = id
        self.arrival_time = arrival_time
        self.cpu_burst = cpu_burst
        self.cpu_burst_needed = cpu_burst
        self.waiting_time: int = 0
        self.turnaround_time: int = 0
        self.time_executed: list[int] = []
        self.shift: list[int] = []
        Task.tasks.append(self)

    @staticmethod
    def check_id_exists(id: str) -> bool:
        for task in Task.tasks:
            if task.id == id:
                return True
        return False
    
    @staticmethod
    def clear_tasks() -> None:
        Task.tasks.clear()

    def __str__(self) -> str:
        return f"""ID: {self.id}
Arrival Time: {self.arrival_time}
CPU Burst: {self.cpu_burst}
CPU Burst Needed: {self.cpu_burst_needed}
Waiting Time: {self.waiting_time}
Turnaround Time: {self.turnaround_time}
Time Executed: {self.time_executed}
Time Shifted: {self.shift}
"""

    def __repr__(self) -> str:
        return self.__str__()


class algo_printer:
    util = algo_util()

    def html_gant_printer(self, gant_string, task_list):
        final_string = ""
        str_list = [char for char in gant_string]
        current_char = str_list[0]
        current_char_count = 0
        time_stamps = []
        start_time = min(task.arrival_time for task in task_list)
        current_time = start_time
        time_stamps.append(current_time)

        for char in str_list:
            if current_char == char:
                current_char_count += 1
            else:
                final_string += current_char
                current_time += current_char_count
                time_stamps.append(current_time)

                current_char = char
                current_char_count = 1

        # Append the last character and time
        if current_char:
            final_string += current_char
            current_time += current_char_count
            time_stamps.append(current_time)

        # Start building the HTML for the Gantt chart
        table_html = '<table class="table-auto mx-auto">\n<tr>\n'
        
        # Loop through the final_string to create table cells
        for char in final_string:
            table_html += f'<td class="w-10 h-9 p-4 border border-pink-500 bg-pink-100 text-pink-700 text-xl font-semibold align-middle">{char}</td>\n'
        
        table_html += '</tr>\n</table>\n'
        
        # Generate the time labels below the Gantt chart
        table_html += '<div class="absolute w-full top-full mt-1 flex justify-center space-x-2">\n'
        for time in time_stamps:
            table_html += f'<div class="w-10 text-center text-pink-700 font-semibold">{time}</div>\n'
        table_html += '</div>\n'
        
        return table_html

    def gant_printer(self, gant_string):
        final_string = ""
        str_list = [char for char in gant_string]
        current_char = None
        current_char_count = 0

        for char in str_list:
            if current_char == char:
                current_char_count += 1
            else:
                if current_char:
                    final_string += "|"
                    for x in range(current_char_count):
                        if x == current_char_count // 2:
                            if current_char == "-":
                                final_string += "@"
                            else:
                                final_string += current_char
                        else:
                            if current_char == "-":
                                final_string += "@"
                            else:
                                final_string += "-"
                    current_char_count = 0  # Reset count for the new character

                current_char = char
                current_char_count = 1

        # Append the remaining characters after the loop ends
        if current_char:
            final_string += "|"
            for x in range(current_char_count):
                if x == current_char_count // 2:
                    final_string += current_char
                else:
                    if current_char == "-":
                        final_string += " "
                    else:
                        final_string += "-"

        final_string += "|"
        print(final_string)
        return final_string

    def turnaround_printer(self, task_list: list[Task]):
        turnaround_list = []
        turnaround_str = "Turnaround Time:\n"
        for task in task_list:
            turnaround_list.append(task.turnaround_time)
            turnaround_str += f"TA {task.id.lower()} = {task.turnaround_time}ms\n"

        turnaround_str += f"Average TA: {self.util.avg(turnaround_list)}ms"
        ave_ta = f"{self.util.avg(turnaround_list)} ms"
        print(turnaround_str)

        return ave_ta

    def waiting_time_printer(self, task_list: list[Task]):
        waiting_time = []
        waiting_time_str = "Waiting Time:\n"
        for task in task_list:
            waiting_time.append(task.waiting_time)
            waiting_time_str += f"WT {task.id.lower()} = {task.waiting_time}ms\n"

        waiting_time_str += f"Average WT: {self.util.avg(waiting_time)}ms"
        ave_wt = f"{self.util.avg(waiting_time)} ms"
        print(waiting_time_str)

        return ave_wt
        

class Algorithm:
    printer = algo_printer()
    util = algo_util()

    def fcfs(self, task_list):
        counter = 0
        queue = []
        gant_string: str = ""
        current_task: Task = None
        finished_tasks = []
        task_list = sorted(task_list, key=lambda x: x.arrival_time)
        copy_task_list = task_list[:]

        while len(finished_tasks) != len(task_list):
            if copy_task_list:
                queue, copy_task_list = self.add_to_queue(copy_task_list, counter, queue)

            if queue:
                if self.check_first_in_q(queue, counter) and not current_task:
                    current_task = queue.pop(0)
                    current_task.time_executed.append(counter)
                    current_task.waiting_time = self.util.task_waiting_time(counter, current_task.arrival_time)

            if current_task:
                gant_string += current_task.id
                current_task.cpu_burst_needed -= 1
                current_task, finished_tasks = self.process_finished_task(current_task, finished_tasks, counter)

            counter += 1  # Increment counter regardless of tasks

        gant_chart = self.printer.html_gant_printer(gant_string, task_list)
        ave_ta = self.printer.turnaround_printer(task_list)
        ave_wt = self.printer.waiting_time_printer(task_list)
        self.revert_cpu_burst(task_list)

        return task_list, gant_chart, ave_ta, ave_wt

    def spf(self, task_list):
        counter = 0
        queue = []
        gant_string: str = ""
        current_task: Task = None
        finished_tasks = []
        task_list: list[Task] = sorted(task_list, key=lambda x: x.arrival_time)
        copy_task_list = task_list[:]

        while len(finished_tasks) != len(task_list):

            # if there are still tasks in task list append it to queue if the first index of the task_list.arrival time == is equal to the counter
            if copy_task_list:
                queue, copy_task_list = self.add_to_queue(copy_task_list, counter, queue)

            # if queue has tasks
            if queue:
                # check our current task
                # sort our queue by cpu burst
                queue = sorted(queue, key=lambda x: x.cpu_burst)

                # check first in q and if we dont have a current task if both are true
                if not current_task:
                    # current task will be the first in q then change task attributes
                    current_task = queue.pop(0)
                    current_task.time_executed.append(counter)
                    current_task.waiting_time = self.util.task_waiting_time(counter, current_task.arrival_time)

            if current_task:
                gant_string += current_task.id
                current_task.cpu_burst_needed -= 1
                current_task, finished_tasks = self.process_finished_task(current_task, finished_tasks, counter)

            counter += 1  # Increment counter regardless of tasks

        self.printer.gant_printer(gant_string)
        ave_ta = self.printer.turnaround_printer(task_list)
        ave_wt = self.printer.waiting_time_printer(task_list)
        self.revert_cpu_burst(task_list)
        gant_chart = self.printer.html_gant_printer(gant_string, task_list)

        return task_list, gant_chart, ave_ta, ave_wt


    def srtf(self, task_list):
        counter = 0
        queue = []
        gant_string = ""
        current_task: Task = None
        finished_tasks = []
        task_list = sorted(task_list, key=lambda x: x.arrival_time)
        copy_task_list = task_list[:]

        while len(finished_tasks) != len(task_list) and counter < 50:
            if copy_task_list:
                queue, copy_task_list = self.add_to_queue(copy_task_list, counter, queue)

            if queue:
                queue = sorted(queue, key=lambda x: x.cpu_burst_needed)
                c_shortest: Task = queue[0]

                if not current_task or c_shortest.cpu_burst_needed < current_task.cpu_burst_needed:
                    if current_task:
                        current_task.shift.append(counter)
                        queue.append(current_task)
                    current_task = queue.pop(0)
                    current_task.time_executed.append(counter)
                    if len(current_task.time_executed) > 1:
                        waiting_time_y = current_task.time_executed[-1] - current_task.shift[-1]
                        current_task.waiting_time = current_task.waiting_time + waiting_time_y
                    else:
                        current_task.waiting_time = self.util.task_waiting_time(counter, current_task.arrival_time)

            if current_task:
                gant_string += current_task.id
                current_task.cpu_burst_needed -= 1

                if current_task.cpu_burst_needed <= 0:
                    current_task.shift.append(counter + 1)
                    current_task.turnaround_time = self.util.task_turnaround_time(counter + 1,
                                                                                  current_task.arrival_time)
                    finished_tasks.append(current_task)
                    current_task = None

            counter += 1
            print(counter)
            print([task.id for task in copy_task_list])
            print([task.id for task in queue])
            print([task.id for task in finished_tasks])

        self.printer.gant_printer(gant_string)
        ave_ta = self.printer.turnaround_printer(task_list)
        ave_wt = self.printer.waiting_time_printer(task_list)
        self.revert_cpu_burst(task_list)
        gant_chart = self.printer.html_gant_printer(gant_string, task_list)

        return task_list, gant_chart, ave_ta, ave_wt

    def revert_cpu_burst(self, task_list: list[Task]):
        for task in task_list:
            task.cpu_burst_needed = task.cpu_burst

    def add_to_queue(self, task_list, counter, queue):
        added_tasks = []
        while task_list and task_list[0].arrival_time == counter:
            added_tasks.append(task_list.pop(0))
        if added_tasks:
            queue.extend(added_tasks)
        return queue, task_list

    def check_first_in_q(self, queue: list[Task], counter):
        if queue and queue[0].arrival_time <= counter:
            return True
        return False

    def process_finished_task(self, current_task: Task, finished_tasks: list[Task], counter):
        if current_task.cpu_burst_needed == 0:
            current_task.shift.append(counter + 1)
            current_task.turnaround_time = self.util.task_turnaround_time(counter + 1, current_task.arrival_time)
            finished_tasks.append(current_task)
            current_task = None

        return current_task, finished_tasks


algorithm = Algorithm()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        Task.clear_tasks()
        tasks = []
        task_count = int(request.form['task_count'])
        for i in range(task_count):
            id = request.form[f'id_{i}']
            arrival_time = int(request.form[f'arrival_time_{i}'])
            cpu_burst = int(request.form[f'cpu_burst_{i}'])
            task = Task(id, arrival_time, cpu_burst)
            tasks.append(task)
        
        selected_algo = request.form['algorithm']
        if selected_algo == 'fcfs':
            task_list, gant_chart, ave_ta, ave_wt = algorithm.fcfs(tasks)
            selected_algo = 'FCFS'
        elif selected_algo == 'spf':
            task_list,gant_chart, ave_ta, ave_wt = algorithm.spf(tasks)
            selected_algo = 'SPF'
        elif selected_algo == 'srtf':
            task_list,gant_chart, ave_ta, ave_wt = algorithm.srtf(tasks)
            selected_algo = 'SRTF'

        return render_template('index.html', task_list = task_list, gant_chart = gant_chart, algo = selected_algo, ave_ta = ave_ta, ave_wt = ave_wt)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
