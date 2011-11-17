#!/usr/bin/python

##
# This Bash script checks if a process is running.  If the process is alive,
# it runs an optional alive command. If the process isn't running, then the
# script instead runs the dead command.
#
# Basic usage:
# ./dead_or_alive.py 1378 -d "echo dead" -a "echo alive"
#
# Run the dead command only if multiple pids are dead:
# ./dead_or_alive.py 1378 1391 -d "echo dead" -a "echo alive"
#
# Check pids from a file:
# ./dead_or_alive.py $(cat pids.txt) -d "echo dead" -a "echo alive"
#
# Check pids from a file, and only consider it alive if at least 25% of them are alive:
# ./dead_or_alive.py $(cat pids.txt) -d "echo dead" -a "echo alive" -t 0.25
##

import commands
import optparse

def is_running(pid):
  """Returns True if a process pid exists, False otherwise."""
  pid = int(pid)
  return len(commands.getoutput("ps -p %i  | grep %i" % (pid, pid))) != 0

def make_arguments():
  """Returns a dict with the shell arguments, specifically pids, alive, dead, and threshold."""
  parser = optparse.OptionParser("usage: %prog [options] arg1 arg2")
  parser.add_option("-a", "--alive", dest="alive",
                    help="command to run if alive")
  parser.add_option("-d", "--dead", dest="dead",
                    help="command to run if dead")
  parser.add_option("-t", "--threshold", dest="threshold",
                    default=0.99999, type="float",
                    help="threshold determines the fraction of processes that must be dead in order to trigger the dead command. Defaults to 0.99999.")

  (options, args) = parser.parse_args()

  if len(args) == 0:
    parser.error("Must provide at least one argument for the process id.")
  
  return {
    'pids': args,
    'alive': options.alive,
    'dead': options.dead,
    'threshold': options.threshold
  }
  
def main():
  arguments = make_arguments()
  
  alive_command = arguments['alive']
  dead_command = arguments['dead']
  threshold = arguments['threshold']
  pids = arguments['pids']
  
  pids_if_running = map(is_running, pids)
  count_trues = lambda count, boolean: count + int(boolean)
  alive_count = reduce(count_trues, pids_if_running)
  
  # There are alive_count running, out of len(pids) total.
  denominator = len(pids) or 1
  percent_alive = float(alive_count) / denominator
  
  if percent_alive < threshold:
    # Qualifies as dead
    if dead_command:
      print commands.getoutput(dead_command)
  else:
    if alive_command:
      print commands.getoutput(alive_command)
  
if __name__ == "__main__":
  main()
