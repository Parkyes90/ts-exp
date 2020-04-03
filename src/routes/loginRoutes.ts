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

router.get("/", (req, res) => {
  if (req.session && req.session.loggedIn) {
    return res.send(`
      <div>
        <div>Your are logged in </div>
        <a href="/auth/logout">Logout</a>
      </div>
    `);
  }
  return res.send(`
      <div>
        <div>Your are not logged in </div>
        <a href="/auth/login">Login</a>
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
