import { defineStore } from 'pinia';
import { authService } from '@/services/auth/authService';

export const useUserStore = defineStore('user', {
    state: () => ({
        user: null,
        role: null,
        token: localStorage.getItem('token') || localStorage.getItem('auth_token') || null,
        studentProfile: null,
        instructorProfile: null,
        isLoading: false,
        error: null,
    }),

    persist: {
        key: 'user-store',
        storage: localStorage,
        paths: ['user', 'role', 'token', 'studentProfile', 'instructorProfile'],
    },

    getters: {
        isAuthenticated: (state) => !!state.token,
        isStudent: (state) => state.role === 'student' || (state.user?.role === 'student'),
        isInstructor: (state) => state.role === 'instructor' || (state.user?.role === 'instructor'),
        userFullName: (state) => {
            if (!state.user) return '';
            return `${state.user.first_name || ''} ${state.user.last_name || ''}`.trim();
        },
        userInitials: (state) => {
            if (!state.user?.username) return 'U';
            return state.user.username[0].toUpperCase();
        }
    },

    actions: {
        setAuth(authData) {
            this.token = authData.token;
            this.user = authData.user;
            this.role = authData.role;
            this.error = null;

            // Keep localStorage in sync for now for any legacy code
            localStorage.setItem('token', authData.token);
            localStorage.setItem('auth_token', authData.token);
            localStorage.setItem('user', JSON.stringify(authData.user));
            localStorage.setItem('user_data', JSON.stringify(authData.user));
            localStorage.setItem('role', authData.role);
        },

        async fetchUserProfile() {
            if (!this.token) return;

            this.isLoading = true;
            try {
                const response = await authService.getUserProfile();
                this.user = response.data;
                // The endpoint api/auth/users/me/ might not return role directly, 
                // handle appropriately based on backend response structure
                if (this.user.role) this.role = this.user.role;

                localStorage.setItem('user', JSON.stringify(this.user));
                localStorage.setItem('user_data', JSON.stringify(this.user));
            } catch (error) {
                console.error('Failed to fetch user profile:', error);
                this.error = error.message;
                if (error.response?.status === 401) {
                    this.logout();
                }
            } finally {
                this.isLoading = false;
            }
        },

        async ensureUserLoaded() {
            if (this.token && !this.user) {
                await this.fetchUserProfile();
            }
        },

        setStudentProfile(profile) {
            this.studentProfile = profile;
            localStorage.setItem('student_data', JSON.stringify(profile));
        },

        logout() {
            this.user = null;
            this.role = null;
            this.token = null;
            this.studentProfile = null;
            this.instructorProfile = null;

            localStorage.clear();
            sessionStorage.clear();

            // The router will handle redirection based on auth state
        }
    }
});
