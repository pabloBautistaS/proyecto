#include "contiki.h"
#include "net/routing/routing.h"
#include "random.h"
#include "net/netstack.h"
#include "net/ipv6/simple-udp.h"
#include "net/ipv6/uip.h"
#include "net/ipv6/sicslowpan.h"
#include "dev/uart1.h"
#include "leds.h"
#include "sys/log.h"
#include "dev/serial-line.h"
#include "dev/sensor/sht11/sht11-sensor.h"

#define LOG_MODULE "App"
#define LOG_LEVEL LOG_LEVEL_INFO
#define UART_BUFFER_SIZE 5

#define WITH_SERVER_REPLY  1
#define UDP_CLIENT_PORT	4949
#define UDP_SERVER_PORT	5678

#define SEND_INTERVAL		  (10 * CLOCK_SECOND)
/*----------------VARIABLE-DE-UART-------------------------------------------*/
static uint8_t rx_buf[UART_BUFFER_SIZE];
static uint8_t index_rx_buf = 0;
char *hum;
char id = 'p';
unsigned int temp;
static int def_rt_rssi = 0;
/*---------------------------------------------------------------------------*/
static struct simple_udp_connection udp_conn;

/*---------------------------------------------------------------------------*/
PROCESS(udp_client_process, "UDP client");
AUTOSTART_PROCESSES(&udp_client_process);
/*------------------------------SENSOR-TEMP-------------------------------------*/
static int
get_temp(void)
{
  return ((sht11_sensor.value(SHT11_SENSOR_TEMP) / 10) - 396) / 10;
}

/*----------------------DATOS-RECIBIDOS-UART---------------------------------*/

int serial_input_byte(unsigned char c)
{
    rx_buf[index_rx_buf]= c;

      while (index_rx_buf < 4){
              rx_buf[index_rx_buf]= c;
              index_rx_buf++;
              break;
           }
      if ( index_rx_buf == 4){
              printf("%s,\n",rx_buf);
              index_rx_buf=0;
              return (rx_buf[index_rx_buf]);
           }
       return 0;
}

/*---------------------------------------------------------------------------*/
static void
udp_rx_callback(struct simple_udp_connection *c,
         const uip_ipaddr_t *sender_addr,
         uint16_t sender_port,
         const uip_ipaddr_t *receiver_addr,
         uint16_t receiver_port,
         const uint8_t *data,
         uint16_t datalen)
{

  LOG_INFO("Received response '%.*s' from ", datalen, (char *) data);
  LOG_INFO_6ADDR(sender_addr);
#if LLSEC802154_CONF_ENABLED
  LOG_INFO_(" LLSEC LV:%d", uipbuf_get_attr(UIPBUF_ATTR_LLSEC_LEVEL));
#endif
  LOG_INFO_("\n");

}
/*---------------------------------------------------------------------------*/
PROCESS_THREAD(udp_client_process, ev, data)
{
  static struct etimer periodic_timer;
  static unsigned count;
  static char str[32];
  uip_ipaddr_t dest_ipaddr;

  PROCESS_BEGIN();

    SENSORS_ACTIVATE(sht11_sensor);
    uart1_init(BAUD2UBR(115200));
    serial_line_init();
    uart1_set_input(serial_input_byte);
//    uart1_set_input(serial_input_byte);


  /* Initialize UDP connection */
  simple_udp_register(&udp_conn, UDP_CLIENT_PORT, NULL,
                      UDP_SERVER_PORT, udp_rx_callback);

  etimer_set(&periodic_timer, random_rand() % SEND_INTERVAL);
   hum = (char*)rx_buf;
   temp = get_temp();

  while(1) {
    PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&periodic_timer));

    if(NETSTACK_ROUTING.node_is_reachable()) {
       def_rt_rssi = sicslowpan_get_last_rssi();
      /* Send to DAG root */
      LOG_INFO("Sending request %u to ", count);
 //     hum = (char*)rx_buf;
      LOG_INFO("humedad %s,\n",hum );
      uip_ip6addr(&dest_ipaddr, 0xbbbb,0,0,0,0,0,0,1);
      LOG_INFO_6ADDR(&dest_ipaddr);
      LOG_INFO_("\n");
      snprintf(str, sizeof(str), "hello %d |%c|%s|%d|", count,id,hum,def_rt_rssi);
      simple_udp_sendto(&udp_conn, str, strlen(str), &dest_ipaddr);
      count++;
    } else {
      LOG_INFO("Not reachable yet\n");
      LOG_INFO("humedad %s %i,\n",hum,temp);
    }

    /* Add some jitter */
    etimer_set(&periodic_timer, SEND_INTERVAL
      - CLOCK_SECOND + (random_rand() % (2 * CLOCK_SECOND)));
  }

  PROCESS_END();
}
/*---------------------------------------------------------------------------*/
