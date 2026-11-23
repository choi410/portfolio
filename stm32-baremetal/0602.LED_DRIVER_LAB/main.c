#include "device_driver.h"

#if 0
void Main(void)
{
	volatile int i, j;

	LED_Init();

	for(i=0;i<16;i++)
	{
		LED_Display(i);
		for(j=0; j<0x40000; j++);
	}

	for(;;)
	{
		LED_All_Off();
		for(j=0; j<0x20000; j++);

		LED_All_On();
		for(j=0; j<0x20000; j++);
	}
}
#endif
void Main(void)
{
	Uart_Init(115200);
		
	/* 이 부분은 수정하지 말 것 */
	Macro_Set_Bit(RCC->APB2ENR, 3);
	Macro_Write_Block(GPIOB->CRH, 0xff, 0x66, 0);
    Macro_Write_Block(GPIOB->ODR, 0x3, 0x2, 8);
	/* Macro를 이용하여 LED0을 ON, LED1을 OFF로 하는 코드를 설계하시오 */


}