/*
제출용

#include <device_driver.h>

// 여기에 사용자 임의의 define을 작성하시오

typedef volatile unsigned int * pReg_t;

#define GPIOB_CRH (*(pReg_t)0x40010C04)
#define GPIOB_ODR (*(pReg_t)0x40010C0C)
#define RCC_APB2ENR   (*(pReg_t)(0x40021000 + 0x18)) // RCC 레지스터 정의가 없다면 추가

void Main(void)
{
      // 이 부분은 임의로 바꾸지 마시오
      RCC_APB2ENR |= (1<<3);

      // GPB[9:8]을 출력 모드로 설정하시오
      // 경고: 이 코드는 다른 핀 설정을 초기화합니다.
      GPIOB_CRH = 0x00000066; 

      // GPB[9:8]에 LED0은 OFF, LED1은 ON 시키도록 설정하시오
      // 경고: 0x100은 LED0 ON, LED1 OFF (요구사항과 다름)
      // 경고: 다른 핀 출력을 모두 LOW로 초기화합니다.
      GPIOB_ODR = 0x00000200;
}
      */


/*
개인용 양쪽으로 깜빡거림

#include <device_driver.h>

// =========================================================
// 여기에 사용자 임의의 define을 작성하시오
// =========================================================

// 레지스터 포인터 타입 정의
typedef volatile unsigned int * pReg_t;

// 레지스터 주소 정의 (이전에 확인된 STM32F103 기반 주소)
#define GPIOB_CRH (*(pReg_t)0x40010C04)
#define GPIOB_ODR (*(pReg_t)0x40010C0C)
#define RCC_APB2ENR   (*(pReg_t)(0x40021000 + 0x18)) 

// =========================================================

// 딜레이 함수 정의 (소프트웨어 루프를 사용하여 시간 지연)
void Delay(volatile unsigned int count)
{
    // 5,000,000 대신 2,500,000으로 줄여서 대략적인 0.5초를 맞춥니다.
    while(count--); 
}


void Main(void)
{
    // 이 부분은 임의로 바꾸지 마시오
    RCC_APB2ENR |= (1<<3); // GPIOB 클럭 활성화

    // -------------------------------------------------------------
    // GPB[9:8]을 출력 모드로 설정하시오
    // -------------------------------------------------------------
    // **경고**: 다른 핀 설정을 모두 초기화하는 방식입니다.
    GPIOB_CRH = 0x00000066; 

    // -------------------------------------------------------------
    // 무한 루프 시작: LED1과 LED2를 교차로 깜빡이도록 설정 (0.5초 주기)
    // -------------------------------------------------------------
    while(1)
    {
        // 1. LED1 ON (GPB9 HIGH), LED2 OFF (GPB8 LOW)
        // GPB9 (2^9 = 0x200)만 HIGH
        GPIOB_ODR = 0x00000200; 

        // 0.5초 대기
        Delay(2500000); 

        // 2. LED1 OFF (GPB9 LOW), LED2 ON (GPB8 HIGH)
        // GPB8 (2^8 = 0x100)만 HIGH
        GPIOB_ODR = 0x00000100;

        // 0.5초 대기
        Delay(2500000);
    }
}

*/

/*

#include <device_driver.h>

// 이 부분은 임의로 바꾸지 마시오
#define RCC_APB2ENR   (*(volatile unsigned long*)0x40021018)

// 여기에 사용자 임의의 define을 작성하시오
#define GPIOB_CRH (*(volatile unsigned long *)0x40010C04)
#define GPIOB_ODR (*(volatile unsigned long *)0x40010C0C)

void Main(void)
{
	  // 이 부분은 임의로 바꾸지 마시오
	  RCC_APB2ENR |= (1<<3);

	  // GPB[9:8]을 출력 모드로 설정하시오

	  GPIOB_CRH = 0x00000066;

	  // GPB[9:8]에 LED0은 OFF, LED1은 ON 시키도록 설정하시오

	  GPIOB_ODR = 0x00000100;
}
      */

      #include "device_driver.h"

void Main(void)
{
	Uart_Init(115200);
	
	/* 이 부분은 임의로 바꾸지 마시오 */
	RCC->APB2ENR |= (1<<3);

	/* 비트 연산을 이용하여 LED0을 ON, LED1을 OFF로 하는 코드를 설계하시오 */


    GPIOB->CRH = (GPIOB->CRH & ~(0xff<<0)) | (0x66<<0);
    GPIOB->ODR = (GPIOB->ODR & ~(0x3<<8)) | (0x2<<8);
	

}