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
      path: '/feed-ceneo',
      name: 'feed-ceneo',
      component: () => import('../views/seo/FeedCeneoPage.vue'),
    },
    {
      path: '/feed-google-shopping',
      name: 'feed-google-shopping',
      component: () => import('../views/seo/FeedGoogleShoppingPage.vue'),
    },
    {
      path: '/feed-allegro',
      name: 'feed-allegro',
      component: () => import('../views/seo/FeedAllegroPage.vue'),
    },
    {
      path: '/integracja-shoper',
      name: 'integracja-shoper',
      component: () => import('../views/seo/IntegracjaShoperPage.vue'),
    },
    {
      path: '/integracja-woocommerce',
      name: 'integracja-woocommerce',
      component: () => import('../views/seo/IntegracjaWooCommercePage.vue'),
    },
    {
      path: '/porownanie/feedy-vs-datafeedwatch',
      name: 'feedy-vs-datafeedwatch',
      component: () => import('../views/seo/PorownanieDataFeedWatchPage.vue'),
    },
    {
      path: '/blog',
      name: 'blog',
      component: () => import('../views/blog/BlogListView.vue'),
    },
    {
      path: '/blog/jak-dodac-produkty-do-ceneo',
      name: 'blog-ceneo',
      component: () => import('../views/blog/JakDodacProduktyDoCeneo.vue'),
    },
    {
      path: '/blog/jak-stworzyc-feed-xml',
      name: 'blog-feed-xml',
      component: () => import('../views/blog/JakStworzycFeedXml.vue'),
    },
    {
      path: '/blog/ceneo-odrzuca-oferty',
      name: 'blog-ceneo-odrzuca',
      component: () => import('../views/blog/CeneoOdrzucaOferty.vue'),
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
