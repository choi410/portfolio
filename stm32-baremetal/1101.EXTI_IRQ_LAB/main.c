#include "device_driver.h"

static void Sys_Init(void)
{
	Clock_Init();
	LED_Init();
	Uart_Init(115200);
	Key_Poll_Init();

	SCB->VTOR = 0x08003000;
	SCB->SHCSR = 0;
}

void Main(void)
{
	Sys_Init();
	Uart1_Printf("EXTI Test\n");

	Macro_Set_Bit(RCC->APB2ENR,3);
	Macro_Set_Bit(RCC->APB2ENR,0);

	Macro_Write_Block(GPIOB->CRL,0xff,0x44,24);
	Macro_Write_Block(AFIO->EXTICR[1],0xff,0x11,8);
	Macro_Write_Block(EXTI->FTSR,0x3,0x3,6);
	Macro_Write_Block(EXTI->IMR,0x3,0x3,6);

	EXTI->PR = (0x3<<6);
	NVIC_ClearPendingIRQ(23);
	NVIC_EnableIRQ(23);

	for(;;)
	{
		LED_Display(1);
		TIM2_Delay(500);
		LED_Display(2);
		TIM2_Delay(500);
	}
}
