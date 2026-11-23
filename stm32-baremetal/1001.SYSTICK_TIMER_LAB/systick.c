#include "device_driver.h"

static void Sys_Init(void)
{
    Clock_Init();
    LED_Init();
    Uart_Init(115200);
    Key_Poll_Init();
}

void sand_timer(unsigned int n) // n msec
{
    SysTick->CTRL = 0x0;
    SysTick->LOAD = 9000 * n; 
    SysTick->VAL = 0;
    
    // SysTick 타이머 시작 (ENABLE SET)
    SysTick->CTRL |= (1U << 0);
}

int sand_timer_timeout(void)
{
    // COUNTFLAG (16번 비트) 추출
    return Macro_Extract_Area(SysTick->CTRL, 0x1, 16);
}

