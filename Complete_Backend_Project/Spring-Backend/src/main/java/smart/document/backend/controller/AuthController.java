package smart.document.backend.controller;

import smart.document.backend.dto.AuthResponse;
import smart.document.backend.dto.LoginRequest;
import smart.document.backend.dto.SignupRequest;
import smart.document.backend.service.AuthService;

import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/auth")
public class AuthController {

    private final AuthService authService;

    public AuthController(AuthService authService) {
        this.authService = authService;
    }

    @PostMapping("/signup")
    public AuthResponse signup(@RequestBody SignupRequest request) {

        System.out.println("========== SIGNUP ENDPOINT HIT ==========");

        return authService.signup(request);
    }

    @PostMapping("/login")
    public AuthResponse login(@RequestBody LoginRequest request) {

        System.out.println("========== LOGIN ENDPOINT HIT ==========");

        return authService.login(request);
    }
}