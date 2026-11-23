#include "device_driver.h"

static void Sys_Init(void)
{
	Clock_Init();
	LED_Init();
	Uart_Init(115200);
	Key_Poll_Init();
}

void Main(void)
{
	void Main(void)
{
    Sys_Init();
    
    // Uart1_Printf 사용 가정
    Uart1_Printf("모래시계\n"); 

    for(;;)
    {
        // 1초 타이머 설정 및 시작 (반복적인 1초 간격 보장)
        sand_timer(1000); 
        
        // 타임아웃이 될 때까지 대기 (COUNTFLAG == 1)
        while(!(sand_timer_timeout() == 1));
        
        // 1초 경과 후 메시지 출력
        Uart1_Printf(" . ");
    }
}
}
