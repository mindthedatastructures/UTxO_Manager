import json
import os
import re
import stat
import shutil

import subprocess
import pathlib

maindir = str(pathlib.Path(__file__).parent.resolve().parent.absolute().parent.absolute())

from src.model.user_model import UserModel
from src.model.tx.utxo_model import UtxoModel
from src.model.tx.policy_model import PolicyModel
from src.model.tx.token_model import TokenModel

from enum import IntEnum


class CliException(Exception):
    def a():
        None

def run(app,cmd):
    env = os.environ
    if app.isMainnet():
        env["CARDANO_NODE_SOCKET_PATH"] = f'{app.config["mainnet_socket"]}'
    else:
        env["CARDANO_NODE_SOCKET_PATH"] = f'{app.config["main_folder"]}/{app.config["socket"]}'
    if not app.silent:
        print('**********')
        print(cmd)
    result = subprocess.run(cmd, env=env, stdout=subprocess.PIPE, stderr = subprocess.PIPE, shell=True)
    if not app.silent:
        print(result)
    if len(result.stderr.decode('utf-8')) > 0 :
        raise CliException(result.stderr.decode('utf-8'))
    return result.stdout.decode('utf-8')

class Application():
    class Modes(IntEnum):
        Testnet=1
        Mainnet=2
    def __init__(self, data_folder='data'):
        self.maindir = maindir
        self.data_folder = data_folder

        with open('config_local.json', 'r') as f:
            self.config = json.loads(f.read())
        if not os.path.exists(f'{maindir}/{self.data_folder}/_tmp'):
            os.makedirs(f'{maindir}/{self.data_folder}/_tmp')

        self.silent = False
        self.mode = Application.Modes.Testnet
        self.mode = Application.Modes.Mainnet

        self.data = {}
        self.loadDefaultData()

        self.users = []
        self.usersOutdated=True
        self.lastModifiedUsersFolder = -1

        self.witness_override = True

        # LISTENERS
        self.mode_changed_listeners = []
        self.request_processed_listeners = []

    #############
    # MODE 

    def setMode(self, mode):
        self.mode = mode
        self.usersOutdated=True
        for l in self.mode_changed_listeners:
            l.updateMode()

    def isMainnet(self):
        return self.mode == Application.Modes.Mainnet

    def getColorForMode(self):
        if self.isMainnet():
            color = '#ffcccc'
        elif self.mode == Application.Modes.Testnet:
            color = '#ddeedd'
        else:
            color = '#ff0000'
        return color

    def prefix(self):
        if self.isMainnet():
            prefix = 'mainnet'
        else:
            prefix = 'testnet'
        return prefix


    #############
    # CONFIG 

    def saveLocalConfig(self):
        with open('config_local.json', 'w') as f:
            f.write(json.dumps(self.config, indent=4))

    #############
    # TESTNET SPECIFICS 

    def getPorts(self):
        nodes = ['node-bft1', 'node-bft2', 'node-pool1']
        res = {}
        for n in nodes:
            with open(f"{self.config['main_folder']}/{n}/port") as f :
                res[n] = f.read()
        return res


    def loadDefaultData(self):
        self.data['faucet_vkey_file'] = 'shelley/utxo-keys/utxo1.vkey'
        self.data['faucet_skey_file'] = 'shelley/utxo-keys/utxo1.skey'
        self.data['faucet_addr_file'] = 'shelley/utxo-keys/utxo1.addr'

    def getTipSlot(self):
        if self.isMainnet:
            cmd = f"{self.config['cardano-cli']} query tip --mainnet"
        else:
            cmd = f"{self.config['cardano-cli']} query tip {self.config['network']}"
        return json.loads(run(self,cmd))['slot']


    def loadLateststLocalTestnetValues(self):
        ## Main_Folder And Magic

        # Main_Folder
        def getKey(x):
            if 'nix-shell.' == x[:10]:
                return os.path.getctime('/tmp/'+x)
            return -1

        def getKey2(x):
            if 'test-' == x[:5]:
                return os.path.getctime('/tmp/'+nixShellDir+'/chairman/'+x)
            return -1
        alls = list(os.listdir('/tmp'))
        alls.sort(key=getKey)
        for a in alls:
            if os.path.exists('/tmp/'+a+'/chairman/'):
                nixShellDir = a
                break
        alls = list(os.listdir('/tmp/'+nixShellDir+'/chairman/'))
        test_dir = max(alls, key=getKey2)
        self.config['main_folder'] = '/tmp/' + nixShellDir + '/chairman/' + test_dir

        # Magic
        cmd = f"{self.config['cardano-cli']} query tip {self.config['network']}"
        try:
            run(self,cmd)
        except Exception as e:
            b = re.search('unNetworkMagic = ([0-9]*)',str(e))
            if b:
                self.config['network'] = f"--testnet-magic {b.groups()[0]}"

    def loadFaucetData(self):
        self.usersOutdated = True
        self.data['faucet_addr'] = self.generateAddressFromVkey(self.config["main_folder"]+'/'+self.data['faucet_vkey_file'])

    #############
    # Address, Users and Key Generation

    def createMainUser(self):
        self.createUser('main_user')

    def createUser(self, username):
        self.usersOutdated = True
        if not os.path.exists(f'{maindir}/{self.data_folder}/_users/{self.prefix()}/{username}'):
            os.makedirs(f'{maindir}/{self.data_folder}/_users/{self.prefix()}/{username}')
        self.keygen(f'{maindir}/{self.data_folder}/_users/{self.prefix()}/{username}/payment1.vkey', f'{maindir}/{self.data_folder}/_users/{self.prefix()}/{username}/payment1.skey')

        address = self.generateAddressFromVkey(f'{maindir}/{self.data_folder}/_users/{self.prefix()}/{username}/payment1.vkey')
        with open(f'{maindir}/{self.data_folder}/_users/{self.prefix()}/{username}/payment1.addr', 'w') as f:
            f.write(address)

    def generateAddressFromVkey(self, vkey_file):
        if self.isMainnet():
            cmd = f'{self.config["cardano-cli"]} address build --mainnet --payment-verification-key-file {vkey_file}'
        else:
            cmd = f'{self.config["cardano-cli"]} address build {self.config["network"]} --payment-verification-key-file {vkey_file}'
        output = run(self,cmd)
        return output

    def keygen(self,vkey_path, skey_path):
        cmd = f'{self.config["cardano-cli"]} address key-gen --verification-key-file {vkey_path} --signing-key-file {skey_path}'
        run(self, cmd)

    def keyhash(self,vkey_path):
        cmd = f'{self.config["cardano-cli"]} address key-hash --payment-verification-key-file {vkey_path}'
        return run(self, cmd)


    #############
    # Get Data

    def getProtocolParameters(self):
        cmd = f'{self.config["cardano-cli"]} query protocol-parameters '
        cmd += f'{self.config["network"]} '
        cmd+= f'--out-file {maindir}/{self.data_folder}/protocol_params/protocol.json '
        res = run(self,cmd)

    def getUtxos(self, addr):
        if self.isMainnet():
            cmd = f'{self.config["cardano-cli"]} query utxo --mainnet --address {addr} --out-file {maindir}/{self.data_folder}/_tmp/utxos.json'
        else:
            cmd = f'{self.config["cardano-cli"]} query utxo {self.config["network"]} --address {addr} --out-file {maindir}/{self.data_folder}/_tmp/utxos.json'
        run(self,cmd)
        with open(f'{maindir}/{self.data_folder}/_tmp/utxos.json', 'r') as f:
            utxos_json = json.loads(f.read())
        os.remove(f'{maindir}/{self.data_folder}/_tmp/utxos.json')
        utxos_objects = []
        for k,v in utxos_json.items():
            utxos_objects.append(UtxoModel.from_json(k,v))
        return utxos_objects


    def getMainUser(self):
        if not os.path.exists(f'{maindir}/{self.data_folder}/_users/{self.prefix()}/main_user'):
            return None
        return 'main_user'

    def getAddress(self, name):
        if not os.path.exists(f'{maindir}/{self.data_folder}/_users/{self.prefix()}/{name}'):
            return None
        with open(f'{maindir}/{self.data_folder}/_users/{self.prefix()}/{name}/payment1.addr', 'r') as f:
            res = f.read()
        if res == '':
            res = self.generateAddressFromVkey(f'{maindir}/{self.data_folder}/_users/{self.prefix()}/{name}/payment1.vkey')
            with open(f'{maindir}/{self.data_folder}/_users/{self.prefix()}/{name}/payment1.addr', 'w') as f:
                f.write(res)
        return res

    def getFaucetUser(self):
        faucet_addr = None
        if 'faucet_addr' in self.data.keys():
            faucet_addr = self.data['faucet_addr']
            # self.loadFaucetData()
        return UserModel(f'{self.config["main_folder"]}/shelley/utxo-keys', 'faucet', faucet_addr, 'utxo1')

    def getTestClientUsers(self):
        return list(filter(lambda x : x.name.startswith('TestClient'), self.getUsers()))

    def getUsers(self):
        lastModified = os.stat( f'{maindir}/{self.data_folder}/_users' )[ stat.ST_MTIME ]
        if self.usersOutdated or self.lastModifiedUsersFolder < lastModified:
            print('Updating Users List')
            self.usersOutdated = False
            self.lastModifiedUsersFolder = lastModified
            self.users = []

            if not self.isMainnet():
                self.users.append(self.getFaucetUser())

            others = os.listdir(f'{maindir}/{self.data_folder}/_users/{self.prefix()}')
            for o in others:
                if os.path.exists(f'{maindir}/{self.data_folder}/_users/{self.prefix()}/{o}/payment1.addr'):
                    with open(f'{maindir}/{self.data_folder}/_users/{self.prefix()}/{o}/payment1.addr', 'r') as f:
                        addr = f.read().rstrip()
                else:
                    addr = self.generateAddressFromVkey(f'{maindir}/{self.data_folder}/_users/{self.prefix()}/{o}/payment1.vkey')

                self.users.append(UserModel(f'{maindir}/{self.data_folder}/_users/{self.prefix()}/{o}', o, addr, 'payment1'))
        return self.users


    def getSignedTxs(self):
        os.listdir(f'{maindir}/{self.data_folder}/signed')


    def getBeforeNumberForPolicyId(self, policyid):
        policy = None
        for p in self.getPolicies():
            if p.id == policyid:
                policy = p
                break
        if policy == None:
            raise Exception(f"policy {policy_id} not found.")
        with open(f'{policy.path}/policy.script', 'r') as f:
            a=json.loads(f.read())
        if 'scripts' not in a.keys():
            return None
        for sc in a['scripts']:
            if sc['type'] == 'before':
                return sc['slot']
        return None

    #############
    # Transaction Commands


    def getBuildCommand(self, transaction, extension='draft',withGenesisAndNotProtocolParams=True):
        my_hash = transaction.getHash()
        path = f'{maindir}/{self.data_folder}/_tmp/{my_hash}'
        if not os.path.exists(path):
            os.makedirs(path)
        cmd = f'{self.config["cardano-cli"]} transaction build-raw '
        cmd += f'--fee {transaction.fee} '
        for utxo in transaction.input_utxos:
            cmd += f'--tx-in {utxo.hash} '
        for utxo in transaction.output_utxos:
            cmd += f'--tx-out {utxo.toCommandString()} '
        if transaction.mint != None and transaction.generate_metadata and transaction.generated_metadata != '':
            cmd += f'--metadata-json-file {transaction.generated_metadata} '
        elif transaction.metadata != None and transaction.metadata != '':
            cmd += f'--metadata-json-file {transaction.metadata} '
        if transaction.mint != None:
            policyid = [t['token'].policy_id for t in transaction.mint.tokens][0]
            before = self.getBeforeNumberForPolicyId(policyid)
            if before != None:
                cmd += f'--invalid-hereafter {before} '
                # cmd += f'--witness-override 2 '
       

        if transaction.mint != None:
            cmd += f'--mint {transaction.mint.getCommandStringOfTokens()} '
            cmd += f'--minting-script-file {transaction.mint.policy.path}/policy.script '
        cmd += f'--out-file {path}/{my_hash}.{extension}'
        return cmd

    def build(self, transaction, extension='draft',withGenesisAndNotProtocolParams=True, silent=True):
        my_hash = transaction.getHash()
        cmd = self.getBuildCommand(transaction, extension, withGenesisAndNotProtocolParams)
        self.store_raw_command(cmd, my_hash)
        if not silent:
            print(my_hash)
            print(cmd)
        res = run(self,cmd)

        return my_hash

    def calculateAndUpdateFee(self, transaction, withGenesisAndNotProtocolParams=True):
        extension = 'draft'
        my_hash = self.build(transaction, extension=extension, withGenesisAndNotProtocolParams=withGenesisAndNotProtocolParams)
        cmd = f'{self.config["cardano-cli"]} transaction calculate-min-fee '
        cmd += f'--tx-body-file {maindir}/{self.data_folder}/_tmp/{my_hash}/{my_hash}.{extension} '
        cmd += f'--tx-in-count {len(transaction.input_utxos)} '
        cmd += f'--tx-out-count {len(transaction.output_utxos)} '
        cmd += f'--witness-count 1 '
        cmd += f'--byron-witness-count 0 '
        if self.isMainnet():
            cmd += f'--mainnet '
            cmd += f'--protocol-params-file {maindir}/{self.data_folder}/_protocol_params/mainnet_protocol.json'
        else:
            cmd += f'{self.config["network"]} '
            cmd += f"--genesis {self.config['main_folder']}/shelley/genesis.json "

        res = run(self,cmd)

        transaction.fee = int(res.split()[0])
        return transaction.fee

    def buildAndSendToReadyToSign(self, tx, my_hash):
        os.makedirs(f'{maindir}/{self.data_folder}/ready_to_sign/{my_hash}')
        shutil.copy(f'{maindir}/{self.data_folder}/_tmp/{my_hash}/{my_hash}.raw', f'{maindir}/{self.data_folder}/ready_to_sign/{my_hash}/{my_hash}.raw')
        a = {}
        if tx.mint != None:
            a['policyID'] = [t['token'].policy_id for t in tx.mint.tokens][0]
        a['address'] = [i.address for i in tx.input_utxos][0]
        with open(f'{maindir}/{self.data_folder}/ready_to_sign/{my_hash}/info.json', 'w') as f:
            f.write(json.dumps(a, indent=4))


    def signWithAddressesAndPolicySkeyPath(self, my_hash, extension, addresses, policySkeyPath):
        cmd = f'{self.config["cardano-cli"]} transaction sign '
        cmd+= f'--tx-body-file {maindir}/{self.data_folder}/_tmp/{my_hash}/{my_hash}.{extension} '
        for a in addresses:
            s = self.getUserByAddress(a)
            if s == None:
                raise Exception(f'{a} not found')
            cmd+= f'--signing-key-file {s.getSkeyPath()} '
        if policySkeyPath != None:
            cmd+= f'--signing-key-file {policySkeyPath} '
        if self.isMainnet():
            cmd += '--mainnet '
        else:
            cmd += f'{self.config["network"]} '
        cmd+= f'--out-file {maindir}/{self.data_folder}/_tmp/{my_hash}/{my_hash}.signed'
        res = run(self,cmd)

    def sign(self, my_hash, extension, transaction):
        addresses = [input_u.address for input_u in transaction.input_utxos]
        policySkeyPath = transaction.mint.policy.getSkeyPath() if transaction.mint != None else None
        self.signWithAddressesAndPolicySkeyPath(my_hash, extension, addresses, policySkeyPath)

    def send(self,my_hash):
        extension = 'signed'
        cmd = f'{self.config["cardano-cli"]} transaction submit '
        cmd+= f'--tx-file {maindir}/{self.data_folder}/_tmp/{my_hash}/{my_hash}.{extension} '
        if self.isMainnet():
            cmd += '--mainnet '
        else:
            cmd += f'{self.config["network"]} '
        res = run(self,cmd)

    #############
    # Minting And Policies

    def getPolicies(self):
        policies = []
        policies_folder = f'{maindir}/{self.data_folder}/policies'
        if not os.path.exists(policies_folder):
            os.makedirs(policies_folder)
        polFolders = os.listdir(policies_folder)
        for fold in polFolders:
            policies.append(PolicyModel.fromPath(fold, policies_folder))
        return policies


    def createPolicy(self,name, addr, before):
        policy_path = f'{maindir}/{self.data_folder}/policies/{name}'
        vkey_path   = f'{policy_path}/policy.vkey'
        skey_path   = f'{policy_path}/policy.skey'
        addr_path   = f'{policy_path}/policy.addr'
        script_path = f'{policy_path}/policy.script'
        id_path     = f'{policy_path}/policyID'
        os.makedirs(policy_path)
        if addr == '':
            self.keygen(vkey_path, skey_path)
            addr = self.generateAddressFromVkey(vkey_path)
        else:
            try:
                self.getUtxos(addr)
            except Exception as e:
                raise e3

        # ADDR FILE
        with open(addr_path,'w') as f:
            f.write(addr)

        # SCRIPT FILE
        with open(script_path,'w') as f:
            if before != -1:
                script = {
                    "type": "all",
                    "scripts":
                    [
                      {
                        "type": "before",
                        "slot": before 
                      },
                      {
                        "type": "sig",
                        "keyHash": self.keyhash(vkey_path).split()[0]
                      }
                    ]
                  }
            else:
                script = {"keyHash": self.keyhash(vkey_path).split()[0],"type":"sig"}
                script = {
                    "type": "all",
                    "scripts":
                    [
                      {
                        "type": "sig",
                        "keyHash": self.keyhash(vkey_path).split()[0]
                      }
                    ]
                  }
            f.write(json.dumps(script, indent=2))

        # ID FILE
        with open(id_path,'w') as f:
            cmd = f'{self.config["cardano-cli"]} transaction policyid --script-file {script_path}'
            policyid = run(self,cmd)
            f.write(policyid)

    def getUserByAddress(self,addr):
        addrs = self.getUsers()
        for ad in addrs:
            if ad.addr == addr:
                return ad
        return None

    def getUserByName(self,name):
        addrs = self.getUsers()
        for ad in addrs:
            if ad.name == name:
                return ad
        return None

    def store_raw_command(self, cmd, my_hash):
        path = f'{maindir}/{self.data_folder}/_tmp/{my_hash}/'
        with open(f'{path}/{my_hash}.command', 'w') as f:
            f.write(cmd)

    def decorateUtxoWithBornTransaction(self,utxo):
        if self.isMainnet():
            utxo.decorators['bornTx'] = self.getDb().getBornTransaction(utxo)

    def estimateTxSize(self, my_hash):
        path = f'{maindir}/{self.data_folder}/_tmp/{my_hash}'
        with open(f'{path}/{my_hash}.raw', 'r') as f:
            res = len(json.loads(f.read())['cborHex'])/2 + 200
        return res
