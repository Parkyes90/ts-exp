import "reflect-metadata";
import { AppRouter } from "../../AppRouter";
import { Methods } from "./Methods";
import { MetadataKeys } from "./MetadataKeys";

export function controller(routePrefix: string) {
  return function (target: Function) {
    const router = AppRouter.getInstance();
    for (const key in target.prototype) {
      if (target.prototype.hasOwnProperty(key)) {
        const routerHandler = target.prototype[key];
        const path = Reflect.getMetadata(
          MetadataKeys.path,
          target.prototype,
          key
        );
        const method: Methods = Reflect.getMetadata(
          MetadataKeys.method,
          target.prototype,
          key
        );
        const middlewares =
          Reflect.getMetadata(MetadataKeys.middleware, target.prototype, key) ||
          [];
        if (path) {
          router[method](
            `${routePrefix}${path}`,
            ...middlewares,
            routerHandler
          );
        }
      }
    }
  };
}
