#include "device_driver.h"

static void Sys_Init(void)
{
	Clock_Init();
	LED_Init();
	Key_Poll_Init();
	Uart_Init(115200);
}

void Motor_Init(void)
{
	Macro_Set_Bit(RCC->APB2ENR, 2);  				// Port-A On
	Macro_Write_Block(GPIOA->CRL, 0xFF, 0x22, 8); 	// Push-Pull
	Macro_Clear_Area(GPIOA->ODR, 0x3, 2); 			// Motor Off
}

#define CW		0x1
#define CCW		0x2

void Motor_Run(int dir)
{
	Macro_Write_Block(GPIOA->ODR, 0x3, dir, 2);
}

void Motor_Hold(void)
{
	Macro_Clear_Area(GPIOA->ODR, 0x3, 2);
}

void Main(void)
{
	Sys_Init();
	Uart_Printf("Motor Control\n");

	Motor_Init();

	for(;;)
	{
		char x = Uart1_Get_Char(); 

		switch(x)
		{
			case 'F' : Motor_Hold(); Motor_Run(CW); break;
			case 'R' : Motor_Hold(); Motor_Run(CCW); break;
			case 'S' : Motor_Hold(); break;
			default : Uart_Printf("Command Error!\n");
		}
	}	
}
