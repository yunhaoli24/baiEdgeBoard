PID=`ps -ef | grep helmet_main_process | grep -v "grep" | awk '{print $2}'`
echo "代码PID:${PID}"
kill -9 ${PID}
echo "已杀死！"