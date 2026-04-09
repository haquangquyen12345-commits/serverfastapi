#ifndef WIFI_APP_H
#define WIFI_APP_H

#include "esp_wifi.h"
#include "esp_event.h"

// Thay đổi tên mạng và mật khẩu nhà bạn ở đây
#define WIFI_SSID       "quyendeptraivl"
#define WIFI_PASS       "cccccccc"
#define MAXIMUM_RETRY   5 // Số lần kết nối lại tối đa nếu bị rớt mạng

void wifi_init_sta(void);

#endif