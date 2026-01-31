#include "user.h"

atk_mo395q_socket_t socket_config = {0};

uint32_t DataBuffer[1];

uint8_t IP[4] = {192,168,1,23}, GWIP[4] = {192,168,1,1}, Mask[4] = {255,255,255,0};
uint8_t socket0_send_buf[32];
uint8_t socket0_recv_buf[1024];
uint8_t socket0_send_done = 1;
uint8_t call_name = 255;
uint8_t data_type = 255;
uint8_t status = 0;

extern uint16_t dataBuf[8];

void phy_conn_cb(uint8_t phy_status)
{
  switch(phy_status)
  {
    case ATK_MO395Q_CMD_PHY_10M_FLL:break;
    default:break;
  }
//  TIM1_Update_Interrupt_Enable();
}

void phy_disconn_cb(void)
{
  // 断开
  socket0_send_done = 1;
}

void dhcp_success_cb(uint8_t *ip, uint8_t *gwip, uint8_t *mask, uint8_t *dns1, uint8_t *dns2)
{
    // 连接上
  status = 0;
}

void socket_send_buf_free_cb(atk_mo395q_socket_t *socket)
{
    switch (socket->socket_index)
    {
        case ATK_MO395Q_SOCKET_0:
        {
            socket0_send_done = 1;
            break;
        }
        default:
        {
            break;
        }
    }
}

void socket_recv_cb(atk_mo395q_socket_t *socket)
{
    uint16_t recv_len;
    
    recv_len = atk_mo395q_cmd_get_recv_len_sn(socket->socket_index);
    if (recv_len != 0)
    {
        if (recv_len > (socket->recv.size - 1))
        {
            recv_len = socket->recv.size;
        }
        atk_mo395q_cmd_read_recv_buf_sn(socket->socket_index, recv_len, socket->recv.buf);
        Deal_Recv(socket->recv.buf);
//        socket->recv.buf[recv_len] = '\0';
//        HAL_UART_Transmit(&huart2, socket->recv.buf, sizeof(socket->recv.buf), HAL_MAX_DELAY);
//        printf("%s", socket->recv.buf);
    }
}

void system_init(void)
{
  uint8_t ret;
  uint8_t key;
  
  delay_init(72);
  
  ret = atk_mo395q_init();
  while(ret != 0)
  {
    ret = atk_mo395q_init();
  }
  
  atk_mo395q_net_config(ATK_MO395Q_CMD_ENABLE, NULL, NULL, NULL, phy_conn_cb, phy_disconn_cb, dhcp_success_cb);
  
  socket_config.socket_index = ATK_MO395Q_SOCKET_0;
  socket_config.enable = ATK_MO395Q_ENABLE;
  socket_config.proto = SOCKET_PROTO;
  socket_config.des_ip[0] = SOCKET_DES_IP_1;
  socket_config.des_ip[1] = SOCKET_DES_IP_2;
  socket_config.des_ip[2] = SOCKET_DES_IP_3;
  socket_config.des_ip[3] = SOCKET_DES_IP_4;
  socket_config.des_port = SOCKET_DES_PORT;
  socket_config.sour_port = SOCKET_SOUR_PORT;
  socket_config.send.buf = socket0_send_buf;
  socket_config.send.size = sizeof(socket0_send_buf);
  socket_config.recv.buf =  socket0_recv_buf;
  socket_config.recv.size = sizeof(socket0_recv_buf);
  socket_config.send_buf_free_cb = socket_send_buf_free_cb;
  socket_config.recv_cb = socket_recv_cb;
  atk_mo395q_socket_config(&socket_config);
  
  HAL_Delay(5000);
}

void system_run(void)
{
  atk_mo395q_handler();
  if(status == 0 && TIM1->CNT > 11520)
  {
    TIM1->CNT = 0;
    if(socket0_send_done == 1)
    {
      socket0_send_done = 0;
      socket0_send_buf[0] = 0x02;
      socket0_send_buf[1] = IP[3];
      socket0_send_buf[2] = call_name / 256;
      socket0_send_buf[3] = call_name % 256;
      atk_mo395q_cmd_write_send_buf_sn(ATK_MO395Q_SOCKET_0, socket0_send_buf, sizeof(socket0_send_buf));
    }
  }
//  if(socket0_send_done == 1)
//  {
//    socket0_send_done = 0;
//    atk_mo395q_cmd_write_send_buf_sn(ATK_MO395Q_SOCKET_0, socket0_send_buf, sizeof(socket0_send_buf));
//  }
}

void Deal_Recv(uint8_t *buf)
{
//  TIM1_Update_Interrupt_Disable();
  status = 1;
  if(*buf == SEND_DATA && socket0_send_done == 1)
  {
    socket0_send_done = 0;
    socket0_send_buf[0] = 0x01;                     // 标识为数据报文
    socket0_send_buf[1] = IP[3];                    // 来源IP
    socket0_send_buf[2] = call_name;                // 来源呼号
    socket0_send_buf[3] = data_type;                // 来源数据种类
    for(uint8_t i = 0;i < 8;i++)
    {
      socket0_send_buf[4 + 2 * i] = (dataBuf[i] >> 8) & 0x00FF;
      socket0_send_buf[5 + 2 * i] = (dataBuf[i] & 0x00FF);
    }
    
    atk_mo395q_cmd_write_send_buf_sn(ATK_MO395Q_SOCKET_0, socket0_send_buf, sizeof(socket0_send_buf));
  }
}

void TIM1_Update_Interrupt_Enable(void)
{
  TIM1->SR &= ~(1 << 0);
  TIM1->CNT = 34558;
  TIM1->DIER |= (1 << TIM1_UP_IRQn);
}

void TIM1_Update_Interrupt_Disable(void)
{
  TIM1->DIER &= ~(1 << 0);
  TIM1->SR &= ~(1 << 0);
}