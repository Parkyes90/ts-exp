import { Request, Response } from "express";
import { controller, routeBinder } from "./decorators";
import { Methods } from "./decorators/Methods";
import { bodyValidator } from "./decorators/bodyValidator";

@controller("/auth")
class LoginController {
  @(routeBinder(Methods.get)("/login"))
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

  @(routeBinder(Methods.post)("/login"))
  @bodyValidator("email", "password")
  postLogin(req: Request, res: Response): void {
    const { email, password } = req.body;
    if (email === "hi@hi.com" && password === "password") {
      req.session = { loggedIn: true };
      res.redirect("/");
    } else {
      res.send("Invalid email or password");
    }
  }

  @(routeBinder(Methods.get)("/logout"))
  logout(req: Request, res: Response): void {
    req.session = undefined;
    res.redirect("/");
  }
}
