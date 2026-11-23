#include "device_driver.h"

/*

void Key_Poll_Init(void)
{
	Macro_Set_Bit(RCC->APB2ENR, 3);
	Macro_Write_Block(GPIOB->CRL, 0xff, 0x44, 24);
}

int Key_Get_Pressed(void)
{


}

void Key_Wait_Key_Released(void)
{


}

int Key_Wait_Key_Pressed(void)
{


}
*/
#include "device_driver.h" // (가상 헤더 파일)

/**
 * @brief  KEY0(PB6), KEY1(PB7) 핀을 입력 모드로 초기화합니다.
 * @note   이미지의 구현을 그대로 따릅니다.
 * (0x44는 플로팅 입력, 0x88은 풀업/풀다운 입력)
 */
void Key_Poll_Init(void)
{
    // 1. GPIOB 클럭 활성화 (IOPBEN, 3번 비트)
    Macro_Set_Bit(RCC->APB2ENR, 3);

    // 2. PB6, PB7 핀 설정 (이미지 내용)
    // CNF6/MODE6 (Pin 6) = 0x4 (플로팅 입력)
    // CNF7/MODE7 (Pin 7) = 0x4 (플로팅 입력)
    // 참고: 플로팅 입력은 외부에 풀업 저항이 연결되어 있어야 합니다.
    // 만약 내부 풀업을 사용한다면 (0x88, 24)와 ODR 설정이 필요합니다.
    Macro_Write_Block(GPIOB->CRL, 0xff, 0x44, 24);
}

/**
 * @brief  현재 눌린 키의 상태를 읽어옵니다. (논블로킹)
 * @note   요구사항:
 * - 안 눌림: 0
 * - Key0(PB6) 눌림: 1
 * - Key1(PB7) 눌림: 2
 * - 둘 다 눌림: 3
 * @retval 0, 1, 2, 3 중 하나의 값
 */
int Key_Get_Pressed(void)
{
    int key_val = 0; // 기본값 0

    // Key0(PB6)가 눌렸는지 확인 (눌리면 0V, Clear)
    if (Macro_Check_Bit_Clear(GPIOB->IDR, 6))
    {
        key_val = 1; // 0 + 1 = 1
    }

    // Key1(PB7)이 눌렸는지 확인 (눌리면 0V, Clear)
    if (Macro_Check_Bit_Clear(GPIOB->IDR, 7))
    {
        key_val += 2; // (0 or 1) + 2 = 2 or 3
    }

    return key_val;
}

/**
 * @brief  현재 눌려있는 키가 있다면, 모두 떼어질 때까지 대기합니다. (블로킹)
 * @note   Key_Get_Pressed()의 반환값이 0이 될 때까지 멈춤
 */
void Key_Wait_Key_Released(void)
{
    // Key_Get_Pressed()가 0이 아닐 동안 (즉, 1, 2, 3 중 하나일 때)
    // 이 루프 안에서 멈춰있습니다.
    while (Key_Get_Pressed() != 0)
    {
        // 대기
    }
    // 아무 키도 안 눌리면 (0) 루프를 탈출하고 리턴
}

/**
 * @brief  키가 새로 눌릴 때까지 대기했다가, 눌린 키의 값을 리턴합니다. (블로킹)
 * @note   채터링(떨림)이나 이미 눌린 상태를 방지하기 위해,
 * 먼저 키가 떼어지는 것을 확인한 후, 새로 눌리기를 기다립니다.
 * @retval 1, 2, 3 중 눌린 키의 값
 */
int Key_Wait_Key_Pressed(void)
{
    int key_val = 0;

    // 1. (안전장치) 현재 키가 눌려있다면 떼어질 때까지 먼저 대기
    Key_Wait_Key_Released();

    // 2. 키가 눌릴 때까지 (즉, Key_Get_Pressed()가 0일 동안) 대기
    do
    {
        key_val = Key_Get_Pressed();
    } while (key_val == 0);

    // 3. 키가 눌렸으므로(1, 2, 3) 그 값을 리턴
    return key_val;
}