/*
#include "device_driver.h"

void LED_Init(void)
{
	//다음 코드는 수정하지 마시오
	Macro_Set_Bit(RCC->APB2ENR, 3);



}

void LED_Display(unsigned int num)
{


}

void LED_All_On(void)
{



}

void LED_All_Off(void)
{


}

*/


/*

#include "device_driver.h"

static void Sys_Init(void)
{
    Clock_Init();
    LED_Init();
    Uart_Init(115200);
}

// Key 인식 

#if 1

void Main(void)
{
    Sys_Init();
    Uart_Printf("KEY Input Test #1\n");

    // -------------------------------------------------------------------
    // KEY[1:0], GPB[7:6]을 GPIO 입력으로 선언
    // -------------------------------------------------------------------
    
    // 1. CRH 레지스터: 핀 7 (Bit 28~31), 핀 6 (Bit 24~27) 영역을 0으로 CLEAN
    GPIOB->CRH &= ~((0xF << 28) | (0xF << 24));
    
    // 2. 핀 7, 6을 입력 모드 (Float Input, 0b0100 = 0x4)로 설정
    // 0x4 << 28 : 핀 7 설정
    // 0x4 << 24 : 핀 6 설정
    GPIOB->CRH |= ((0x4 << 28) | (0x4 << 24));

    for(;;)
    {
        // -------------------------------------------------------------------
        // KEY0 (GPB7) 처리: 눌렸으면 Low(0)이 들어옴 (Low-Active)
        // -------------------------------------------------------------------
        // IDR 레지스터의 7번 비트가 0인지 확인
        if (!(GPIOB->IDR & (1 << 7))) 
        {
            // KEY0가 눌렸으면 LED0 (GPB9)를 ON (HIGH로 SET)
            GPIOB->ODR |= (1 << 9); 
        }
        else
        {
            // KEY0가 안 눌렸으면 LED0 (GPB9)를 OFF (LOW로 CLEAR)
            GPIOB->ODR &= ~(1 << 9);
        }
        
        // -------------------------------------------------------------------
        // KEY1 (GPB6) 처리: 눌렸으면 Low(0)이 들어옴 (Low-Active)
        // -------------------------------------------------------------------
        // IDR 레지스터의 6번 비트가 0인지 확인
        if (!(GPIOB->IDR & (1 << 6))) 
        {
            // KEY1이 눌렸으면 LED1 (GPB8)을 ON (HIGH로 SET)
            GPIOB->ODR |= (1 << 8); 
        }
        else
        {
            // KEY1이 안 눌렸으면 LED1 (GPB8)을 OFF (LOW로 CLEAR)
            GPIOB->ODR &= ~(1 << 8);
        }
    }
}

#endif
*/