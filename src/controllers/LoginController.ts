import { Request, Response } from "express";
import { get } from "./decorators";
import { controller } from "./decorators";

@controller("/auth")
class LoginController {
  @get("/login")
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
