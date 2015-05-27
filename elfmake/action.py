"""Represents the action that may be performed to build
the recipes."""

import env
import recipe
import subprocess


def make_line(args):
	line = ""
	for a in args:
		if isinstance(a, list):
			line = line + make_line(a)
		else:
			line = line + " " + env.to_string(a)
	return line

def invoke(*cmd):
	"""Launch the given command in the current shell."""
	line = make_line(cmd)
	print line
	r = subprocess.call(line, shell=True)
	if r <> 0:
		raise env.ElfError("build failed")


class Action:
	"""Base class of all actions."""
	
	def execute(self, ress, deps):
		"""Perform the action. If an action fails, raise env.ElfError exception.
		It takes as parameter the list of results and the list of dependencies."""
		pass


class ShellAction(Action):
	"""An action that invokes a shell command."""
	cmd = None
	
	def __init__(self, cmd):
		self.cmd = cmd

	def execute(self, ress, deps):
		invoke(self.cmd)


class GroupAction(Action):
	"""Represent a group of actions."""
	actions = None
	
	def __init__(self, actions):
		self.actions = actions
	
	def execute(self, ress, deps):
		for action in self.actions:
			action.execute(ress, deps)


class FunAction(Action):
	"""An action that takes a function to execution the action."""
	fun = None
	
	def __init__(self, fun):
		self.fun = fun
	
	def execute(self, ress, deps):
		fun(ress, deps)


def make_actions(*actions):
	result = []
	for action in actions:
		if isinstance(action, list):
			result = result + action
		elif isinstance(action, Action):
			result.append(action)
		else:
			result.append(ShellAction(str(action)))
	if len(result) == 1:
		return result[1]
	else:
		return GroupAction(result)


class ActionRecipe(recipe.Recipe):
	"""A recipe that supports an action. object for generation."""
	act = None
	
	def __init__(self, ress, deps, action):
		recipe.Recipe.__init__(self, ress, deps)
		self.act = action
	
	def action(self):
		self.act.execute(self.ress, self.deps)


def rule(ress, deps, *actions):
	"""Build a rule with actions."""
	ActionRecipe(ress, deps, make_actions(actions))
