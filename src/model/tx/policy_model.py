import os

class PolicyModel():

	def fromPath(name, policies_path):
		p = PolicyModel()
		p.name = name
		p.path = f'{policies_path}/{name}'
		with open(f'{p.path}/policy.addr', 'r') as f:
			p.address = f.read()
		with open(f'{p.path}/policyID', 'r') as f:
			p.id = f.read().split()[0]
		return p


	def __init__(self):
		self.name = ''


	def toString(self):
		return f'{self.name} - {self.id}'

	def getSkeyPath(self):
		return f'{self.path}/policy.skey'

