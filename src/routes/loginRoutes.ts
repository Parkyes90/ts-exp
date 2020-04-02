import { Router, Request, Response, NextFunction } from "express";

interface RequestWithBody extends Request {
  body: { [key: string]: string | undefined };
}

function requiredAuth(req: Request, res: Response, next: NextFunction) {
  if (req.session && req.session.loggedIn) {
    next();
    return undefined;
  }

  res.status(403);
  res.send("Not permitted");
}

const router = Router();

router.get("/login", (req, res) => {
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
});

router.post("/login", (req: RequestWithBody, res) => {
  const { email, password } = req.body;
  if (email && password && email === "hi@hi.com" && password === "password") {
    req.session = { loggedIn: true };
    res.redirect("/");
  } else {
    res.send("Invalid email or password");
  }
});

router.get("/", (req, res) => {
  if (req.session && req.session.loggedIn) {
    return res.send(`
      <div>
        <div>Your are logged in </div>
        <a href="/logout">Logout</a>
      </div>
    `);
  }
  return res.send(`
      <div>
        <div>Your are not logged in </div>
        <a href="/login">Login</a>
      </div>
    `);
});

router.get("/logout", (req, res) => {
  req.session = undefined;
  res.redirect("/");
});

router.get("/protected", requiredAuth, (req, res) => {
  res.send("Welcome to protected route, logged in user");
});

export { router };
