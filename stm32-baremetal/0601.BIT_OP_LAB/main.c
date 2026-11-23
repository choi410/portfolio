/*
#include "device_driver.h"

void Main(void)
{
	Uart_Init(115200);
	
	// 이 부분은 임의로 바꾸지 마시오
	RCC->APB2ENR |= (1<<3);

	//비트 연산을 이용하여 LED0을 ON, LED1을 OFF로 하는 코드를 설계하시오 


    GPIOB->CRH = (GPIOB->CRH & ~(0xff<<0)) | (0x66<<0);
    GPIOB->ODR = (GPIOB->ODR & ~(0x3<<8)) | (0x1<<8);
	

}

*/


#include "device_driver.h"
void Main(void)
{
	volatile int i;

	/* 이 부분은 수정하지 말 것 */
	Macro_Set_Bit(RCC->APB2ENR, 3);

	/* 매크로를 이용하여 초기에 LED 모두 OFF */




	for(;;)
	{
	/* LED 반전 및 Delay, Delay는 0x80000으로 설정 */



	}
}