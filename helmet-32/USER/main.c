#include "led.h"
#include "delay.h"
#include "key.h"
#include "sys.h"
#include "usart.h"
#include "uart2.h"
#include "uart3.h"
#include "timer.h"

 
/************************************************
 ALIENTEK战舰STM32开发板实验4
 串口实验 
 技术支持：www.openedv.com
 淘宝店铺：http://eboard.taobao.com 
 关注微信公众平台微信号："正点原子"，免费获取STM32资料。
 广州市星翼电子科技有限公司  
 作者：正点原子 @ALIENTEK
************************************************/


/*
										TX     RX
串口1 喇叭  		 		PA9   PA10
串口2 EdgeBoard  		PA2   PA3      
串口3 OLED 					PB10  PB11
舵机 								PA1

*/
int main(void)
{		
    u8 t=0;
    delay_init();	    	 //延时函数初始化	  
    NVIC_PriorityGroupConfig(NVIC_PriorityGroup_2); //设置NVIC中断分组2:2位抢占优先级，2位响应优先级
    uart_init(9600);	 //串口初始化为9600
    uart2_Init(9600);
    uart3_Init(9600);
		TIM_SetCompare2(TIM2,800);	
		TIM2_PWM_Init(19999,71);
    LED_Init();			     //LED端口初始化
 	while(1)
	{
//        uart1_test();
        uart2_test();
//        uart3_test();
        delay_ms(5);
        if(++t>100)
        {
            t=0;
            LED0=!LED0;
        }
	}	 
 }

