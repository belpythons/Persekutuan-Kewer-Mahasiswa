export const routes = [
  { path: '/', redirect: '/dashboard' },
  {
    path: '/',
    component: () => import('@/layouts/default.vue'),
    children: [
      {
        path: 'dashboard',
        component: () => import('@/pages/dashboard.vue'),
      },
      {
        path: 'production-capacity',
        component: () => import('@/pages/production-capacity.vue'),
      },
      {
        path: 'global-capacity',
        component: () => import('@/pages/global-capacity.vue'),
      },
      {
        path: 'forecasting-ai',
        component: () => import('@/pages/forecasting-ai.vue'),
      },
      {
        path: 'support-weather-mlops',
        component: () => import('@/pages/support-weather-mlops.vue'),
      },
    ],
  },
  {
    path: '/',
    component: () => import('@/layouts/blank.vue'),
    children: [
      {
        path: 'login',
        component: () => import('@/pages/login.vue'),
      },
      {
        path: 'register',
        component: () => import('@/pages/register.vue'),
      },
      {
        path: '/:pathMatch(.*)*',
        component: () => import('@/pages/[...error].vue'),
      },
    ],
  },
]
