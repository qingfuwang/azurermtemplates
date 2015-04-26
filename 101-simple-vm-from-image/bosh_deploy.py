from Utils.WAAgentUtil import waagent
import Utils.HandlerUtil as Util
import commands
waagent.LoggerInit('/var/log/waagent.log','/dev/stdout')
hutil =  Util.HandlerUtility(waagent.Log, waagent.Error, "bosh-deploy-script")
hutil.do_parse_context("enable")
if not os.file('/bosh_os.tar'):
   call("sh changeOS.sh",shell=True)

from subprocess import call
call("mkdir -p ./bosh/config",shell=True)
call("mkdir -p ./bosh/.ssh",shell=True)

call(["cp","micro_bosh.yml.org","./bosh/config/micro_bosh.yml"])
settings= hutil.get_public_settings()
print str(settings)
for i  in settings.keys():
    if i == 'fileUris':
       continue
    print 'sed -i s/#'+str(i)+'#/'+str(settings[i])+'/ ./bosh/config/micro_bosh.yml'
    call('sed -i s/#'+str(i)+'#/'+str(settings[i])+'/ ./bosh/config/micro_bosh.yml',shell=True)
    call('echo '+str(i)+'  :  '+str(settings[i])+"  >>./bosh/config/settings",shell=True)
    #call('echo '+i+"  ==> "+str(settings[i])+" >> ./bosh/config/settings",shell=True)

call("sh create_cert.sh >> ./bosh/config/micro_bosh.yml",shell=True)
call("chmod 700 myPrivateKey.key",shell=True)
call("cp myPrivateKey.key ./bosh/.ssh/bosh.key",shell=True)
call("cp -r ./bosh /home/"+settings['username'],shell=True)
call("chown -R "+settings['username']+" "+"/home/"+settings['username'],shell=True)

call("/usr/local/bin/azure config mode asm",shell=True)
call("/usr/local/bin/azure storage container --container stemcell -a "+settings['storageaccount']+"-k "++settings['storagekey'],shell=True)
call("/usr/local/bin/azure storage blob copy start  --dest-account-name "+settings['storageaccount']+"  --dest-container stemcell --dest-blob stemcell.vhd --source-uri '"+settings['stemcelluri']+"' --dest-account-key '"+settings['storagekey']+"' --quiet",shell=True)
