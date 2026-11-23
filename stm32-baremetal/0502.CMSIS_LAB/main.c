///*
#include "device_driver.h"

void Main(void)
{
	volatile int i;

	Uart_Init(115200);
	Uart_Printf("CMSIS Based Register Define\n");

	// 이 부분은 수정하지 말 것
	RCC->APB2ENR |= (1<<3);

	// LED Pin을 출력으로 설정
	GPIOB -> CRH =0X66 << 0;
//odr(output data register) gpio 핀의 현재 출력 값을 설정하는 데 사용되는 레지스터
//crh(control register high) gpio 핀의 동작모드(기능)을 설정하는 데 사용되는 레지스터
//8~15를 설정하면 crh 0~7은 crl 담당

	for(;;)
	{
		// LED 모두 ON
		GPIOB -> ODR = 0X0 << 8; // 수정

		for(i=0; i<0x40000; i++);

		// LED 모두 OFF
		GPIOB -> ODR = 0X3 << 8; // 0X3을 8번 밀기.

		for(i=0; i<0x40000; i++);
	}
}
//*/


/*
#include "device_driver.h"

void Main(void)
{
	Uart_Init(115200);
	
	/* 이 부분은 임의로 바꾸지 마시오 */
	RCC->APB2ENR |= (1<<3);

	/* 비트 연산을 이용하여 LED0을 ON, LED1을 OFF로 하는 코드를 설계하시오 */


    GPIOB->CRH = (GPIOB->CRH & ~(0xff<<0)) | (0x66<<0);
    GPIOB->ODR = (GPIOB->ODR & ~(0x3<<8)) | (0x1<<8);
	

}
*/


