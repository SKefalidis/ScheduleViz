from itertools import count
from PyQt5.QtGui import QColor


class ProcessInfo:
    new_id = count(0)

    def __init__(self, name: str, cpu_burst: int, queue_arrival_time: int, color: QColor):
        self.name: str = name
        self.cpu_burst: int = cpu_burst
        self.queue_arrival_time: int = queue_arrival_time
        self.color: QColor = color
        self.uid = next(self.new_id)


class ProcessExecStats:
    def __init__(self, process: ProcessInfo):
        self.process = process
        self.start_time: int = -1  # ms passed till the process gets cpu time for the first time
        self.turnaround_time: int = -1

    def __eq__(self, other):
        return self.process.uid == other.process.uid


class TimeBlock:
    def __init__(self, process: ProcessInfo, process_name: str, duration: int):
        self.duration: int = duration
        self.process: ProcessInfo = process
        self.process_name: str = process_name

    def __str__(self):
        return "Process: {} for {} ms".format(self.process_name, self.duration)

    def __repr__(self):
        return "Process: {} for {} ms".format(self.process_name, self.duration)


class Processor:
    def __init__(self, time_slice: int, context_switch_cost: int):
        self.time_slice: int = time_slice
        self.context_switch_cost: int = context_switch_cost
        self.time_blocks: [TimeBlock] = []
        self.current_process = None

    def exec(self, scheduling, process_info_list: [ProcessInfo]) -> ([TimeBlock], [ProcessExecStats]):
        """
        :param scheduling: Scheduling algorithm
        :param process_info_list: Processes that require cpu time
        :return: (time blocks of cpu usage, execution information about processes)
        """
        processes_stats: [ProcessExecStats] = scheduling(process_info_list, self)
        self.join_time_blocks()
        return self.time_blocks, processes_stats

    def slice_exec(self, p: ProcessInfo) -> (ProcessInfo, int):
        """
        :param p: Process to execute
        :return: (changed process p, time elapsed)
        """
        if p is None:
            self.time_blocks.append(TimeBlock(None, "None", 1))
            self.current_process = None
            return None, 1  # we want to check every ms for a new process in the queue

        context_switched = False
        if p != self.current_process and p is not None:  # no context switch required when a process terminates and another doesn't start
            self.time_blocks.append(TimeBlock(None, "CS", 1))
            context_switched = True
        cpu_time = 0
        if p.cpu_burst < self.time_slice:
            cpu_time = p.cpu_burst
            p.cpu_burst = 0
        else:
            cpu_time = self.time_slice
            p.cpu_burst -= self.time_slice
        self.time_blocks.append(TimeBlock(p, p.name, cpu_time))
        self.current_process = p
        return p, cpu_time + 1 if context_switched else cpu_time

    def join_time_blocks(self):
        i = 0
        while i < len(self.time_blocks) - 1:
            if self.time_blocks[i].process_name == self.time_blocks[i + 1].process_name:
                self.time_blocks[i].duration += self.time_blocks[i + 1].duration
                self.time_blocks.pop(i + 1)
            else:
                i += 1


def fcfs(process_info_list: [ProcessInfo], cpu: Processor) -> [ProcessExecStats]:
    processes_stats: [ProcessExecStats] = []
    for p in process_info_list:
        processes_stats.append(ProcessExecStats(p))

    timer = 0
    while process_info_list:
        pes: ProcessExecStats = [x for x in processes_stats if x.process.uid == process_info_list[0].uid][0]
        if process_info_list[0].queue_arrival_time <= timer:
            if pes.start_time == -1:
                pes.start_time = timer + 1  # +1 because of the context switch
            process_info_list[0], time_elapsed = cpu.slice_exec(process_info_list[0])
            timer += time_elapsed
            if process_info_list[0].cpu_burst == 0:
                process_info_list.pop(0)
                pes.turnaround_time = timer - pes.process.queue_arrival_time
        else:
            _, time_elapsed = cpu.slice_exec(None)
            timer += time_elapsed

    return processes_stats


def rr(process_info_list: [ProcessInfo], cpu: Processor) -> [ProcessExecStats]:
    processes_stats: [ProcessExecStats] = []
    for p in process_info_list:
        processes_stats.append(ProcessExecStats(p))

    timer = 0
    while process_info_list:
        changed = False
        for p in process_info_list:
            pes: ProcessExecStats = [x for x in processes_stats if x.process.uid == p.uid][0]
            if p.queue_arrival_time <= timer:
                if pes.start_time == -1:
                    pes.start_time = timer + 1  # +1 because of the context switch
                changed = True
                p, time_elapsed = cpu.slice_exec(p)
                timer += time_elapsed
                if p.cpu_burst == 0:
                    process_info_list.remove(p)
                    pes.turnaround_time = timer - pes.process.queue_arrival_time
            else:
                continue
        if not changed:
            _, time_elapsed = cpu.slice_exec(None)
            timer += time_elapsed

    return processes_stats


def sjf(process_info_list: [ProcessInfo], cpu: Processor) -> [ProcessExecStats]:
    processes_stats: [ProcessExecStats] = []
    for p in process_info_list:
        processes_stats.append(ProcessExecStats(p))

    timer = 0
    while process_info_list:
        # find processes that have arrived
        available_processes: [ProcessInfo] = []
        for p in process_info_list:
            if p.queue_arrival_time <= timer:
                available_processes.append(p)
        if not available_processes:  # if there is no process available just skip
            _, time_elapsed = cpu.slice_exec(None)
            timer += time_elapsed
            continue
        # find the process with the smallest cpu burst
        min_process: ProcessInfo = available_processes[0]
        for p in available_processes:
            if p.cpu_burst < min_process.cpu_burst:
                min_process = p
        # execute that process
        pes: ProcessExecStats = [x for x in processes_stats if x.process.uid == min_process.uid][0]
        if pes.start_time == -1:
            pes.start_time = timer + 1  # +1 because of the context switch
        min_process, time_elapsed = cpu.slice_exec(min_process)
        timer += time_elapsed
        if min_process.cpu_burst == 0:
            process_info_list.remove(min_process)
            pes.turnaround_time = timer - pes.process.queue_arrival_time

    return processes_stats
