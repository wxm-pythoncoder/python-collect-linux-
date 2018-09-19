# /usr/bin/env python3
# -*- coding:utf-8 -*-
import platform
import os
import re
import subprocess
import time
'''
package_out函数说明
根据suse厂家说明的获取操作系统
创建时间的方法同时获得每个安装包
以及安装的时间的键值对
然后将时间+7
在遍历这个键值对，对于这个值
便是所有在系统安装超过
7天之后的安装包
'''

def package_out():
    d1={"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,"Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12}
    e={}
    l=[]
    result=subprocess.Popen("/bin/rpm -qa --last >/tmp/pack.txt", shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    time.sleep(3)
    with open('/tmp/pack.txt','r') as f:
        for i in f.readlines():
            i=i.strip().split()
            m=[i[4],str(d1.get(i[3])),i[2]]
            if i[6] == 'PM':
                i[5]= str(int(i[5].split(':')[0])+12)+':'+i[5].split(':')[1]+':'+i[5].split(':')[2]
            m2='-'.join(m)+' '+i[5]
            #print(m2)
            e[i[0]]=m2
            l.append(m2)
            #print(l)
        #print(e)
        #print(len(e))
    l=sorted(l)
    #print(l)
    #print(l[0])
    L=l[0]
    L_M=['1','3','5','7','8','10','12']
    L_S=['4','6','9','11']
    a,b,c,d=L.split('-')[0],L.split('-')[1],L.split('-')[2].split()[0],L.split('-')[2].split()[1]
    if b==2 and int(c)+7>29:
        T='-'.join([a,str(3),str(int(c)-22)])+' '+d
    elif b==2 and int(c)+7<=29:
        T='-'.join([a,str(2),str(int(c)+7)])+' '+d
    elif b in L_M and int(c)+7<=31:
        T='-'.join([a,str(b),str(int(c)+7)])+' '+d
    elif b in L_M and int(c)+7>31:
        T='-'.join([a,str(int(b+1)),str(int(c)-24)])+' '+d
    elif b in L_S and int(c)+7<=30:
        T='-'.join([a,str(b),str(int(c)+7)])+' '+d
    elif b==2 and int(c)+7>30:
        T='-'.join([a,str(int(b)+1),str(int(c)-23)])+' '+d
    for k,v in e.items():
        if v>T:
           print(k)
# 获取用户相关信息
def get_hosts():
    print('|||hosts_out|||')
    execcom("cat /etc/hosts|grep -v '#'|grep -v '^$'|grep -v 'localhost'")
    print('--------------')


def get_oversion():
    print('|||osversion_out|||')
    if os.path.exists('/etc/centos-release'):
        execcom('cat /etc/centos-release')
    elif os.path.exists('/etc/SuSE-release'):
        execcom('cat /etc/SuSE-release')
    else:
        print('未知的操作系统')
    print('--------------')

#用户
def get_user():
    print('|||group_out|||')
    l = ['bin', 'daemon', 'adm', 'lp', 'sync', 'shutdown', 'halt', 'mail', 'operator', 'games', 'ftp', 'nobody',
         'systemd-bus-proxy', 'systemd-network', 'dbus', 'polkitd', 'abrt', 'unbound', 'usbmuxd', 'tss',
         'libstoragemgmt', 'rpc', 'colord', 'saslauth', 'geoclue', 'setroubleshoot', 'rtkit', 'qemu', 'radvd',
         'chrony', 'ntp', 'sssd', 'rpcuser', 'nfsnobody', 'pulse', 'gdm', 'gnome-initial-setup', 'avahi', 'postfix',
         'sshd', 'tcpdump','nogroup','messagebus','uuidd','polkituser','suse-ncc','haldaemon']
    f = open("/etc/group")
    for i in f.readlines():
        group = i.split(':')[0]
        UID = i.split(':')[2]
        if group not in l and int(UID) >= 500:
            print(group)
    print("|||usr_out|||")
    d = {}
    l1 = []
    l2 = []
    f1 = open("/etc/passwd")
    for line in f1.readlines():
        d[line.split(':')[0]] = line.split(':')[5]  # 把每个用户和家目录生成字典
        if os.path.exists(os.path.join(line.split(":")[5], '.bash_profile')):
            l1.append(line.split(':')[0])  # 如果存在.bashp_profile文件就加入有效用户
        elif os.path.exists(os.path.join(line.split(":")[5], '.profile')):
            l2.append(line.split(':')[0])
    print("|||开始读所有用户的.profile文件|||")
    if len(l1) > 0:
        for i in l1:
            if i == 'root':
                pass
            else:
                print("开始读%s的环境变量" % i)
                execcom('cat' + ' ' + d.get(i) + '/.bash_profile' + '|' + "grep -v '#'" + '|' + "grep -v '^$'")
                print("-------------")
    if len(l2) > 0:
        for i in l2:
            if i == 'root':
                pass
            else:
                print("开始读%s的环境变量" % i)
            execcom('cat' + ' ' + d.get(i) + '/.profile' + '|' + "grep -v '#'" + '|' + "grep -v '^$'")
            print("-------------")

    print("|||开始读所有用户的cron信息|||")
    # 扩展l2到l1
    l1.extend(l2)
    for i in l1:
        print("开始读%s的cron信息" % i)
        execcom(('su - ' + i + ' -l -c ' + '"crontab -l"'))
        print('--------------')
    print("|||开始读所有用户的umask信息|||")
    for i in l1:
        print('开始读%s的umask信息' % i)
        execcom('su - ' + i + ' -l -c ' + '"umask"')
        print('--------------')


# 读文件函数
def readfile(filename):
    if os.path.exists(filename):
        f = open(filename)
        lines = f.readlines()
        for line in lines:
            if line.__contains__("#"):
                continue
            print(line.strip())
        f.close()
    else:
        print("文件" + filename + "不存在")


# 执行操作系统级别的命令,尽量不使用os.system()，容易报一些莫名其妙的错误
def execcom(cwd):
    s = os.popen(cwd)
    print(s.read())
    s.close()


# 需求字典,有需要添加进去
d = {
    'hostname': 'hostname',  # 不变
    'kernel': 'sysctl -a',  # 不知道怎么变
    'vg': ['lvs', 'vgs'],  # 测试环境没有做逻辑分卷
    'fstab': '/etc/fstab',  # 不变
    'df': "df -lh|awk -F ' ' '{print$1,$6}'",  # 不变
    'ifconfig': "ifconfig|grep 'inet'|grep -v 'inet6'|grep -v 'inet 127.0.0.1'",  # 只获得各个网卡的IP,子网掩码,和默认网关
    'route': 'netstat -r',  # 都要
    'syslog': '/etc/syslog-ng/syslog-ng.conf',  # 配置文件,测试环境不存在
    'mail': ['/etc/sysconfig/mail', '/etc/sendmail.cf'],  # 配置文件,测试环境不存在
    'services': "chkconfig --list",  # 获取所有开机项
    'ntp': ['/etc/ntp.conf'],  # 配置文件可以，测试环境没有ntp服务
    'env': '/etc/environment',  # 测试机为空
    'passwd': ['/etc/login.defs', '/etc/pam.d/common-auth'],
    'limit': ['/etc/hosts.allow', '/etc/host.deny'],  # 配置文件不变
}
if __name__ == '__main__':
	#获取操作系统安装时间之后一个星期的安装包
	package_out()
    # 获取操作系统版本
    get_oversion()
    # 执行用户函数
    get_user()
    # 获取hosts的信息
    get_hosts()
    # 执行字典里面的内容
    for k in d.keys():
        if isinstance(d[k], list):
            print('|||' + str(k) + '_out' + '|||')
            for i in d[k]:
                if i.__contains__('/'):
                    readfile(i)
                    print('--------------')

                else:
                    execcom(i)
                    print('--------------')

        else:
            if '/' in d[k]:
                print('|||' + str(k) + '_out' + '|||')
                readfile(d[k])
                print('--------------')

            else:
                print('|||' + str(k) + '_out' + '|||')
                execcom(d.get(k))
                print('--------------')

    # 无法在配置字典里面的单独显示
    print('|||service_out|||')
    execcom(" cat /etc/services|grep -v '#'|grep -v '^$' ")
    print('--------------')
# 集群配置
#note
##服务器是否的搭建集群信息命令
'''
rcopenais status

一
返回的状态
1如果是Running
2就拿配置文件
步骤1 crm_mon -1 |#grep online输出online节点信息
步骤2  后期根据需求筛选
二
返回的状态 stopped
/hostname
打印主机名
三
如果没有装集群
输出该系统不属于集群
'''



    print("cluster_out")
    nodeos=execcom("cat /etc/*release|tail -3|head -1|cut -d ' ' -f 1")
    if nodeos == 'SUSE':
        os.popen("crm configure show > /tmp/cluster.txt")
        readfile("/tmp/cluster.txt")
        print('--------------')
        os.remove("/tmp/cluster.txt")
    else:
        print('该操作系统不支持集群')

