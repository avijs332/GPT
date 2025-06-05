export const Welcome = () => {
  return (
    <div className="welcome">
      <h1>Welcome to Our Application!</h1>
      <p>
        This is the starting point of your journey. Please choose an option to
        proceed:
      </p>
      <ul>
        <li>
          <a href="/login">Login</a>
        </li>
        <li>
          <a href="/register">Register</a>
        </li>
      </ul>
    </div>
  );
}