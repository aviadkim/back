import rtlPlugin from 'stylis-plugin-rtl';
import { CacheProvider } from '@emotion/react';
import createCache from '@emotion/cache';
import { prefixer } from 'stylis';

// קונפיגורציה עבור אחסון CSS בזיכרון המכיל את הכללים עבור RTL
const rtlCache = createCache({
  key: 'muirtl',
  stylisPlugins: [prefixer, rtlPlugin],
});

// קומפוננט עוטף עבור תמיכה ב-RTL
const RTL = (props) => {
  return <CacheProvider value={rtlCache}>{props.children}</CacheProvider>;
};

export { rtlCache, RTL }; 