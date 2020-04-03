import "reflect-metadata";
import { AppRouter } from "../../AppRouter";

export function controller(routePrefix: string) {
  return function (target: Function) {
    const router = AppRouter.getInstance();
    for (const key in target.prototype) {
      if (target.prototype.hasOwnProperty(key)) {
        const routerHandler = target.prototype[key];
        const path = Reflect.getMetadata("path", target.prototype, key);
        if (path) {
          router.get(`${routePrefix}${path}`, routerHandler);
        }
      }
    }
  };
}
