import json  #处理json文件
import paramiko  #链接服务器
import os
import re  #处理正则表达式

json_dir = "/root/test1/1.json"  #配置json文件
local_dir = "/root/test1/"  #本地存放文件目录


def connect(host, port=22, username='root', password='aaaaaaa'):  #链接服务器
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  #生成ssh对象等
    try:
        ssh.connect(host, port, username, password)  #测试链接
        print('connect success')
        return ssh  #成功返回连接ssh对象
    except Exception as e:
        print('connect erro', e)
        return None  #错误返回空


def command(args, outpath):  #拼接命令
    cmd = '%s %s' % (outpath, args)
    return cmd


def exec_commands(conn, cmd):  #执行命令
    stdin, stdout, stderr = conn.exec_command(cmd)
    results = stdout.read()
    return results  #返回命令执行结果


def excutor(host, port, username, password, outpath, args):  #调佣执行命令函数将结果处理返回
    conn = connect(host, port, username, password)
    if not conn:
        return None
    # exec_commands(conn,'chmod +x %s' % outpath)
    cmd = command(args, outpath)
    result = exec_commands(conn, cmd)
    result = json.dumps(result.decode(encoding="utf-8"),
                        indent=4,
                        ensure_ascii=False)

    return result


def copy_module(conn, inpath, outpath):  #使用paramiko库自带SFTP传输文件
    ftp = conn.open_sftp()
    ftp.get(inpath, outpath)  #从服务器到本地
    #ftp.put(inpath, outpath)#从本地到服务器
    ftp.close()
    return outpath


def read_json():  #打开json文件并处理
    with open(json_di, 'r+') as f:
        load_dict = json.load(f)
    return load_dict


if __name__ == '__main__':
    load_dict = read_json()
    for i in load_dict:  #遍历配置
        prefix = i['prefix']
        server_ip = i['server_ip']
        server_dir = i["server_dir"]
        server_port = i["server_port"]
        username = i['username']
        password = i['password']
        result = excutor(server_ip, server_port, username, password, 'ls ',
                         server_dir)
        result_lis = result.split('\\n')  #返回的结果 每个文件名之间有换行 用来分隔
        conn = connect(server_ip, server_port, username, password)
        for j in result_lis:
            #             print(j)
            if re.match(r'(\S)*(\d{4}-\d{1,2}-\d{1,2})', j,
                        flags=0) and prefix in j:  #先用正则匹配年月 再用 in 匹配前缀
                print('success')
                print(
                    copy_module(conn, server_dir + j,
                                local_dir + server_ip + j))