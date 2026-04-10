import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'landing',
      component: () => import('../views/LandingView.vue'),
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/RegisterView.vue'),
    },
    {
      path: '/forgot-password',
      name: 'forgot-password',
      component: () => import('../views/ForgotPasswordView.vue'),
    },
    {
      path: '/reset-password',
      name: 'reset-password',
      component: () => import('../views/ResetPasswordView.vue'),
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('../views/DashboardView.vue'),
      meta: { auth: true },
    },
    {
      path: '/feeds-in/new',
      name: 'feed-in-create',
      component: () => import('../views/FeedInCreateView.vue'),
      meta: { auth: true },
    },
    {
      path: '/feeds-in/:id',
      name: 'feed-in-detail',
      component: () => import('../views/FeedInDetailView.vue'),
      meta: { auth: true },
    },
    {
      path: '/feeds-out/new',
      name: 'feed-out-create',
      component: () => import('../views/FeedOutCreateView.vue'),
      meta: { auth: true },
    },
    {
      path: '/feeds-out/:id',
      name: 'feed-out-detail',
      component: () => import('../views/FeedOutDetailView.vue'),
      meta: { auth: true },
    },
    {
      path: '/organization',
      name: 'organization',
      component: () => import('../views/OrganizationView.vue'),
      meta: { auth: true },
    },
    {
      path: '/polityka-prywatnosci',
      name: 'privacy-policy',
      component: () => import('../views/PrivacyPolicyView.vue'),
    },
    {
      path: '/regulamin',
      name: 'terms',
      component: () => import('../views/TermsView.vue'),
    },
    {
      path: '/polityka-cookies',
      name: 'cookie-policy',
      component: () => import('../views/CookiePolicyView.vue'),
    },
  ],
})

router.beforeEach((to) => {
  const token = localStorage.getItem('access_token')

  if (to.meta.auth && !token) {
    return { name: 'login' }
  }

  if (to.name === 'landing' && token) {
    return { name: 'dashboard' }
  }
})

export default router
