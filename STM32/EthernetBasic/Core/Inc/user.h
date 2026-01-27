#include "main.h"
#include "atk_mo395q.h"
#include "usart.h"
#include "adc.h"
#include "tim.h"

#define SOCKET_PROTO ATK_MO395Q_SOCKET_UDP
#define SOCKET_DES_IP_1  192
#define SOCKET_DES_IP_2  168
#define SOCKET_DES_IP_3  1
#define SOCKET_DES_IP_4  2
#define SOCKET_DES_PORT  8080
#define SOCKET_SOUR_PORT 8081

#define SEND_DATA 0xFF

void system_init(void);
void system_run(void);
void Deal_Recv(uint8_t *buf);
void TIM1_Update_Interrupt_Enable(void);
void TIM1_Update_Interrupt_Disable(void);