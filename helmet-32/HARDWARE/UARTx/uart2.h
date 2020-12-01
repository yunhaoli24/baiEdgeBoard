#ifndef UART2_H
#define UART2_H

#include "sys.h"
#include "stdarg.h"	 	 
#include "stdio.h"	 	 
#include "string.h"

#define USART2_REC_LEN  			200  	//定义最大接收字节数 200
	  	
extern u8  USART2_RX_BUF[USART2_REC_LEN]; //接收缓冲,最大USART_REC_LEN个字节.末字节为换行符 
extern u16 USART2_RX_STA;         		//接收状态标记	


void uart2_Init(u32 baudrate);
void uart2_test(void);
void u2_printf(char *fmt,...);

#endif
