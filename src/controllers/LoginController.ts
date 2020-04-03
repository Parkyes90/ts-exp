import { NextFunction, Request, Response } from "express";
import { controller, routeBinder, use } from "./decorators";
import { Methods } from "./decorators/Methods";

function logger(req: Request, res: Response, next: NextFunction) {
  console.log("Request was made!!!");
  next();
}

@controller("/auth")
class LoginController {
  @(routeBinder(Methods.get)("/login"))
  @use(logger)
  getLogin(req: Request, res: Response): void {
    res.send(`
          <form method="POST">
              <div>
                <label>Email</label>
                <input type="text" name="email">
              </div>
              <div>
                <label>Password</label>
                <input type="password" name="password">
                <button>Submit</button>
              </div>
          </form>
  `);
  }
}
