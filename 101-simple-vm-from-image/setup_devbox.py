from Utils.WAAgentUtil import waagent
import Utils.HandlerUtil as Util
import commands
import os
import re
import json
waagent.LoggerInit('/var/log/waagent.log','/dev/stdout')
hutil =  Util.HandlerUtility(waagent.Log, waagent.Error, "bosh-deploy-script")
hutil.do_parse_context("enable")
#if not os.file('/bosh_os.tar'):
#   call("sh changeOS.sh",shell=True)

from subprocess import call
call("mkdir -p ./bosh",shell=True)
call("mkdir -p ./bosh/.ssh",shell=True)


settings= hutil.get_public_settings()

for f in ['micro_bosh.yml','update_os.sh','deploy_micro_bosh.sh','install_bosh_client.sh']:
    with open (f,"r") as tmpfile:
        content = tmpfile.read()
    for i  in settings.keys():
        if i == 'fileUris':
           continue
        content=re.compile(re.escape("#"+i+"#"), re.IGNORECASE).sub(settings[i],content)
    with open (os.path.join('bosh',f),"w") as tmpfile:
        tmpfile.write(content)

with open (os.path.join('bosh','settings'),"w") as tmpfile:
    tmpfile.write(json.dumps(settings, indent=4, sort_keys=True))

call("sh create_cert.sh >> ./bosh/micro_bosh.yml",shell=True)
call("chmod 700 myPrivateKey.key",shell=True)
call("cp myPrivateKey.key ./bosh/.ssh/bosh.key",shell=True)
call("cp -r ./bosh /home/"+settings['username'],shell=True)
call("chown -R "+settings['username']+" "+"/home/"+settings['username'],shell=True)
call("sh bosh/install_bosh_client.sh",shell=True)
call("/usr/local/bin/azure config mode asm",shell=True)
call("/usr/local/bin/azure storage container create --container stemcell -a "+settings['storageaccount']+"-k "+settings['storagekey'],shell=True)
call("/usr/local/bin/azure storage blob copy start  --dest-account-name "+settings['storageaccount']+"  --dest-container stemcell --dest-blob stemcell.vhd --source-uri '"+settings['stemcelluri']+"' --dest-account-key '"+settings['storagekey']+"' --quiet",shell=True)
exit(0)
