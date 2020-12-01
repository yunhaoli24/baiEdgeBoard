#include "uart2.h"
#include "usart.h"	
#include "uart3.h"
#include "delay.h"


u8  USART2_RX_BUF[USART2_REC_LEN]; //接收缓冲,最大USART_REC_LEN个字节.末字节为换行符 
u16 USART2_RX_STA;         		//接收状态标记	
u8  	Warning_sign=0;

void uart2_Init(u32 baudrate)
{
    GPIO_InitTypeDef GPIO_InitStructure;
    USART_InitTypeDef USART_InitStructure;
    NVIC_InitTypeDef NVIC_InitStructure;
    
    RCC_APB1PeriphClockCmd(RCC_APB1Periph_USART2, ENABLE);
    RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA, ENABLE);	//使能USART2，GPIOA时钟

    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_2; //PA.2
    GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_AF_PP;	//复用推挽输出
    GPIO_Init(GPIOA, &GPIO_InitStructure);//初始化GPIOA.2

    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_3;//PA3
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_IN_FLOATING;//浮空输入
    GPIO_Init(GPIOA, &GPIO_InitStructure);//初始化GPIOA.3  

    //Usart1 NVIC 配置
    NVIC_InitStructure.NVIC_IRQChannel = USART2_IRQn;
    NVIC_InitStructure.NVIC_IRQChannelPreemptionPriority=3 ;//抢占优先级3
    NVIC_InitStructure.NVIC_IRQChannelSubPriority = 3;		//子优先级3
    NVIC_InitStructure.NVIC_IRQChannelCmd = ENABLE;			//IRQ通道使能
    NVIC_Init(&NVIC_InitStructure);	//根据指定的参数初始化VIC寄存器

    //USART 初始化设置

    USART_InitStructure.USART_BaudRate = baudrate;//串口波特率
    USART_InitStructure.USART_WordLength = USART_WordLength_8b;//字长为8位数据格式
    USART_InitStructure.USART_StopBits = USART_StopBits_1;//一个停止位
    USART_InitStructure.USART_Parity = USART_Parity_No;//无奇偶校验位
    USART_InitStructure.USART_HardwareFlowControl = USART_HardwareFlowControl_None;//无硬件数据流控制
    USART_InitStructure.USART_Mode = USART_Mode_Rx | USART_Mode_Tx;	//收发模式

    USART_Init(USART2, &USART_InitStructure); //初始化串口2
    USART_ITConfig(USART2, USART_IT_RXNE, ENABLE);//开启串口接受中断
    USART_Cmd(USART2, ENABLE);                    //使能串口2
}

void USART2_IRQHandler(void)                	//串口2中断服务程序
{
	u8 Res;

    if(USART_GetITStatus(USART2, USART_IT_RXNE) != RESET)  //接收中断(接收到的数据必须是0x0d 0x0a结尾)
    {
        Res =USART_ReceiveData(USART2);	//读取接收到的数据

        if((USART2_RX_STA&0x8000)==0)//接收未完成
        {
            if(USART2_RX_STA&0x4000)//接收到了0x0d
            {
                if(Res!=0x62)USART2_RX_STA=0;//接收错误,重新开始
                else USART2_RX_STA|=0x8000;	//接收完成了 
            }
            else //还没收到0X0D
            {	
                if(Res==0x61)USART2_RX_STA|=0x4000;
                else
                {
                    USART2_RX_BUF[USART2_RX_STA&0X3FFF]=Res ;
                    USART2_RX_STA++;
                    if(USART2_RX_STA>(USART2_REC_LEN-1))USART2_RX_STA=0;//接收数据错误,重新开始接收	  
                }		 
            }
        }   		 
    } 

} 
static u8 USART2_TX_BUF[200];

void u2_printf(char* fmt,...)  
{     
	u16 i,j; 
	va_list ap; 
	va_start(ap,fmt);
	vsprintf((char*)USART2_TX_BUF,fmt,ap);
	va_end(ap);
	i=strlen((const char*)USART2_TX_BUF);		//此次发送数据的长度
	for(j=0;j<i;j++)							//循环发送数据
	{
		while((USART2->SR&0X40)==0);			//循环发送,直到发送完毕   
		USART2->DR=USART2_TX_BUF[j];  
	} 
}
void uart2_test(void)
{
	u32 len,t;
	static u32 times=0;
	if(USART2_RX_STA&0x8000)
	{					   
		len=USART2_RX_STA&0x3fff;//得到此次接收到的数据长度
		for(t=0;t<1;t++)
        {
					if(USART2_RX_BUF[0]=='0')
					{
						printf("关门");
						delay_ms(200);
						close_page();
						TIM_SetCompare2(TIM2,500);	
						delay_ms(500);
						Warning_sign=0;
					}
					if(USART2_RX_BUF[0]=='1')
					{
						printf("开门");
						delay_ms(200);
						open_page();
						TIM_SetCompare2(TIM2,1500);	
						delay_ms(500);
						Warning_sign=0;
					
					}
					if(USART2_RX_BUF[0]=='3')
					{
						main_page();
						TIM_SetCompare2(TIM2,500);
						if(Warning_sign==5)
						{
							printf("请佩戴安全帽");
						delay_ms(200);
						delay_ms(500);
						Warning_sign=0;
						}
						else
							Warning_sign++;
					
					}

        }
//		u2_printf("\r\n\r\n");//插入换行
		USART2_RX_STA=0;
	}else
	{
		times++;
//		if(times%200==0)u2_printf("usart2:请输入数据,以回车键结束\r\n");  
	}
}

