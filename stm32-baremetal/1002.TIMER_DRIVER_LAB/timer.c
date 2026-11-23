#include "device_driver.h"
// #include "system_config.h" // TIMXCLK 정의가 포함되어 있다고 가정

#define TIM2_TICK       (20)                 // usec (1 틱당 20 마이크로초)
#define TIM2_FREQ       (1000000 / TIM2_TICK) // 50000 Hz (50 kHz)
#define TIM2_MAX        (0xFFFF)             // 최대 카운트 값 (65535)

// TIMXCLK는 시스템 클록(예: 84,000,000 Hz)으로 정의되어 있다고 가정

void TIM2_Stopwatch_Start(void)
{
    // 1. TIM2 주변 장치 클록 활성화 (RCC->APB1ENR의 0번 비트)
    Macro_Set_Bit(RCC->APB1ENR, 0);

    // 2. TIM2 CR1 설정: 
    //   - OPM=1 (3번 비트): One Pulse Mode (0 도달 시 자동 정지)
    //   - DIR=1 (4번 비트): Down Counter
    //   - ARPE=0 (7번 비트): ARR Preload Disable (설정값 즉시 반영)
    //   -> (1 << 3) | (1 << 4) = 0x18
    TIM2->CR1 = (1 << 3) | (1 << 4) | (0 << 7);

    // 3. ARR 초기값 설정: 최대값 (0xFFFF)
    TIM2->ARR = TIM2_MAX;

    // 4. PSC 초기값 설정: 20usec tick (50KHz)이 되도록 계산
    // PSC = (TIMXCLK / TIM2_FREQ) - 1
    // (예: 84MHz / 50kHz) - 1 = 1680 - 1 = 1679
    // +0.5를 더해 반올림 효과를 주어 정확도를 높이는 방식 (int) 형변환 시 발생할 수 있는 오차 줄이기)
    // TIMXCLK 정의가 없으므로 계산식은 그대로 유지함
    TIM2->PSC = (unsigned short)(((double)TIMXCLK / (double)TIM2_FREQ) + 0.5) - 1;

    // 5. UG (Update Generation) 이벤트 발생: 설정 값들을 CNT에 즉시 반영
    Macro_Set_Bit(TIM2->EGR, 0); 

    // 6. TIM2 start: CEN (0번 비트)를 Set
    Macro_Set_Bit(TIM2->CR1, 0);
}

// -------------------------------------------------------------

unsigned int TIM2_Stopwatch_Stop(void)
{
    unsigned int time;
    unsigned int current_cnt; // 32비트 타이머일 수 있으므로 int로 변경

    // 1. TIM2 stop: CEN (0번 비트)를 Clear하여 타이머 정지
    Macro_Clear_Bit(TIM2->CR1, 0);

    // 2. 현재 CNT 값 읽기
    current_cnt = TIM2->CNT;

    // 3. 경과 시간 계산: 
    // 경과 펄스 수 = 시작 펄스 수 (ARR) - 현재 남은 펄스 수 (CNT)
    // 시간 (usec) = 경과 펄스 수 * 20 usec/펄스
    time = (TIM2->ARR - current_cnt) * TIM2_TICK;

    return time;
}

void TIM2_Delay(int time)
{
    // 상수 정의 (함수 외부 또는 상단에 정의되어 있다고 가정)
    #define TIM2_TICK_US       (20)
    #define TIM2_FREQ_HZ       (1000000 / TIM2_TICK_US) // 50,000 Hz
    #define TIM2_CLK_HZ        (84000000)           // 시스템 클록 주파수 (예: 84MHz)
    
    // 1. TIM2 클록 활성화
    Macro_Set_Bit(RCC->APB1ENR, 0);

    // 2. TIM2 CR1 설정: down count(DIR=1), one pulse(OPM=1)
    // ARPE=0으로 유지 (기본값)
    TIM2 -> CR1 = (1 << 4) | (1 << 3);

    // 3. PSC 초기값 설정 => 20usec tick이 되도록 설계 (50KHz)
    TIM2->PSC = (TIM2_CLK_HZ / TIM2_FREQ_HZ) - 1;

    // 4. ARR 초기값 설정 => 요청한 time msec에 해당하는 초기값 설정
    // 펄스 수 = time (msec) * 50 (펄스/msec)
    TIM2->ARR = (unsigned short)(time * 50);

    // 5. UG 이벤트 발생 (설정값 CNT에 즉시 반영)
    Macro_Set_Bit(TIM2->EGR, 0);

    // 6. Update Interrupt Pending Clear (이전 UIF 클리어)
    Macro_Clear_Bit(TIM2->SR, 0);

    //7.TIM2 start (CEN=1)
    Macro_Set_Bit(TIM2->CR1,0);

    // 8. Wait timeout: UIF 플래그가 Set될 때까지 대기
    while (!(TIM2->SR & 0x1));

    // 9. Stop and Power off
    // 타이머 정지 (CEN=0)
    Macro_Clear_Bit(TIM2->CR1, 0);
    // 인터럽트 요청 비활성화 (UIE=0)
    Macro_Clear_Bit(TIM2->DIER, 0);
    // (추가) 사용 후 플래그 소거 (다음 사용을 위해)
    Macro_Clear_Bit(TIM2->SR, 0);
}

#define TIM4_TICK_US       (20)                  // 1 틱당 20 마이크로초
#define TIM4_FREQ_HZ       (1000000 / TIM4_TICK_US) // 50,000 Hz
#define TIM4_CLK_HZ        (84000000)            // 시스템 클록 주파수 (예: 84MHz)

void TIM4_Repeat(int time)
{
	Macro_Set_Bit(RCC->APB1ENR, 2);

	// TIM4 CR1: ARPE=0, down counter, repeat mode
	TIM4->CR1 = (1 << 4) | (0 << 3) | (1 << 7);
	// PSC(50KHz),  ARR(reload시 값) 설정
	TIM4->PSC = (TIM4_CLK_HZ / TIM4_FREQ_HZ) - 1;
	TIM4->ARR = (unsigned short)(time * 50);
	// UG 이벤트 발생
	Macro_Set_Bit(TIM4->EGR, 0);
	//Pending clear

	// Update Interrupt Pending Clear
	Macro_Clear_Bit(TIM4->SR, 0);
	// Update Interrupt Enable

	// TIM4 start
	Macro_Set_Bit(TIM4->CR1, 0);
}

int TIM4_Check_Timeout(void)
{
	// 타이머가 timeout 이면 1 리턴, 아니면 0 리턴
	// TIM4 Status Register (SR)의 0번 비트 (UIF)를 확인
    if (TIM4->SR & 0x1) 
    {
        // 타임아웃이면 플래그를 클리어 (다음 타임아웃 감지 준비)
        Macro_Clear_Bit(TIM4->SR, 0); //이것을 안하면 sustick 1번 이후에 타이머만 동작 주의!
        return 1; // 타임아웃 발생
    }
    
    return 0; // 타임아웃 미발생

}

void TIM4_Stop(void)
{
	Macro_Clear_Bit(TIM4->CR1, 0);
	Macro_Clear_Bit(TIM4->DIER, 0);
	Macro_Clear_Bit(RCC->APB1ENR, 2);
}

void TIM4_Change_Value(int time)
{
	TIM4->ARR = 50 * time;
}
