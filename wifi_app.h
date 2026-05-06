#ifndef WIFI_APP_H
#define WIFI_APP_H

#include "esp_wifi.h"
#include "esp_event.h"
#include <stdbool.h>
// Thay đổi tên mạng và mật khẩu nhà bạn ở đây
#define WIFI_SSID       "quyendeptraivl"
#define WIFI_PASS       "cccccccc"
extern bool is_wifi_connected;
void wifi_init_sta(void);

#endif
