package smart.notification.service.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class NotificationController {

    @GetMapping("/api/notifications")
    public String sendNotification(
            @RequestParam String message) {

        return "Notification Service received: " + message;
    }
}