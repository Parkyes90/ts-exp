import { NextFunction, Request, Response } from "express";
import { controller, routeBinder, use } from "./decorators";
import { Methods } from "./decorators/Methods";

export function requiredAuth(req: Request, res: Response, next: NextFunction) {
  if (req.session && req.session.loggedIn) {
    next();
    return undefined;
  }

  res.status(403);
  res.send("Not permitted");
}

@controller("")
class LoginController {
  @(routeBinder(Methods.get)("/"))
  getRoot(req: Request, res: Response): void {
    if (req.session && req.session.loggedIn) {
      res.send(`
      <div>
        <div>Your are logged in </div>
        <a href="/auth/logout">Logout</a>
      </div>
    `);
    } else {
      res.send(`
      <div>
        <div>Your are not logged in </div>
        <a href="/auth/login">Login</a>
      </div>
    `);
    }
  }
  @(routeBinder(Methods.get)("/protected"))
  @use(requiredAuth)
  getProtectedRequireAuth(req: Request, res: Response): void {
    res.send("Welcome to protected route, logged in user");
  }
}
