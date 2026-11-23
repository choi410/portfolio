
/*
#include "device_driver.h"
static void Sys_Init(void)
{
    Clock_Init();
    LED_Init();
    Uart_Init(115200);
}


void Main(void)
{
	Sys_Init();

	Uart_Printf("KEY Input Test #1\n");

	Macro_Write_Block(GPIOB->CRL, 0xFF, 0x44, 24);

	for(;;)
	{
		//스위치가 누를경우 확인 누르면 0 안누르면 1

		if (Macro_Check_Bit_Clear(GPIOB->IDR, 6)) //6번비트가 0인지 체크
		{
			Macro_Clear_Bit(GPIOB->ODR, 8); //led 0 ON
		}

		else 
		{
			Macro_Set_Bit(GPIOB->ODR, 8); ////led 0 OFF
		}

		if (Macro_Check_Bit_Clear(GPIOB->IDR, 7)) //7번비트가 0인지 체크
		{
			Macro_Clear_Bit(GPIOB->ODR, 9);
		}
		
		else
		{
			Macro_Set_Bit(GPIOB->ODR, 9);
		}

		Macro_Write_Block(GPIOB->ODR, 0x3, Macro_Extract_Area(GPIOB->IDR, 0x3, 6), 8);

	}
}

*/
#include "device_driver.h"
static void Sys_Init(void)
{
    Clock_Init();
    LED_Init();
    Uart_Init(115200);
}

void Main(void)
{
	int flag = 0;
	Sys_Init();

	Uart_Printf("KEY Input Toggling #1\n");

	Macro_Write_Block(GPIOB->CRL, 0xFF, 0x44, 24);
/*
	for(;;)
	{
		//방법 1 (실시간성 저해)
		//키0에 눌렸으면 led 0 0n, 안눌렸으면 off

		if (Macro_Check_Bit_Clear(GPIOB->IDR, 6))
		{
			Macro_Invert_Bit(GPIOB->ODR, 8);
			while (Macro_Check_Bit_Clear(GPIOB->IDR, 6));
		}


*/ 
/*

//개인적으로 만든거
		for(;;)
	{
		//방법 1 (실시간성 저해)
		//키0에 눌렸으면 led 0 0n, 안눌렸으면 off

		if(Macro_Check_Bit_Clear(GPIOB->IDR,6))
		{
			Macro_Clear_Bit(GPIOB->ODR, 8);
			//while (Macro_Check_Bit_Clear(GPIOB->IDR, 6));
		}
		else
		{
			Macro_Set_Bit(GPIOB->ODR, 8);
		}

		if(Macro_Check_Bit_Clear(GPIOB->IDR,7))
		{
			Macro_Clear_Bit(GPIOB->ODR, 9);
			//while (Macro_Check_Bit_Clear(GPIOB->IDR, 6));
		}
		else
		{
			Macro_Set_Bit(GPIOB->ODR, 9);
		}
*/
/*
//방법 2 (인터락(변수) 이용)
		
		if ((flag == 0) && Macro_Check_Bit_Clear(GPIOB->IDR, 6))
		{
			Macro_Invert_Bit(GPIOB->ODR, 8);
			flag = 1;
		}
		
		if ((flag == 1) && Macro_Check_Bit_Set(GPIOB->IDR, 6))
		{
			flag = 0;
		}
*/

// [중요] 
// 루프가 반복되어도 값이 유지되어야 하므로, 
// main 함수 안에 선언한다면 'static'으로 선언해야 합니다.
static int key6_flag = 0; // 6번 키의 상태를 기억 (0: 떼어짐, 1: 눌림)
static int key7_flag = 0; // 7번 키의 상태를 기억 (0: 떼어짐, 1: 눌림)

for(;;)
{
    // --- 6번 키 (LED 8번 토글) ---
    
    // 1. 키가 '떼어진(0)' 상태에서 '눌려진(Clear)' 순간을 감지 ⬇️
    if ((key6_flag == 0) && Macro_Check_Bit_Clear(GPIOB->IDR, 6))
    {
        Macro_Invert_Bit(GPIOB->ODR, 8); // LED 8번 상태를 딱 한 번 뒤집기
        key6_flag = 1;                    // 상태를 '눌림(1)'으로 변경 (다시 토글되지 않도록)
    }
    
    // 2. 키가 '눌려진(1)' 상태에서 '떼어진(Set)' 순간을 감지 ⬆️
    if ((key6_flag == 1) && Macro_Check_Bit_Set(GPIOB->IDR, 6))
    {
        key6_flag = 0;                    // 상태를 '떼어짐(0)'으로 리셋 (다음 누름을 받을 준비)
    }

    // --- 7번 키 (LED 9번 토글) ---
    
    // 1. 키가 '떼어진(0)' 상태에서 '눌려진(Clear)' 순간을 감지 ⬇️
    if ((key7_flag == 0) && Macro_Check_Bit_Clear(GPIOB->IDR, 7))
    {
        Macro_Invert_Bit(GPIOB->ODR, 9); // LED 9번 상태를 딱 한 번 뒤집기
        key7_flag = 1;                    // 상태를 '눌림(1)'으로 변경
    }
    
    // 2. 키가 '눌려진(1)' 상태에서 '떼어진(Set)' 순간을 감지 ⬆️
    if ((key7_flag == 1) && Macro_Check_Bit_Set(GPIOB->IDR, 7))
    {
        key7_flag = 0;                    // 상태를 '떼어짐(0)'으로 리셋
    }

    // ... (프로그램이 멈추지 않고 다른 작업도 수행 가능) ...
}
		
	}

