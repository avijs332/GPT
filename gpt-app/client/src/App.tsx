import { AppProviders } from "./providers"
import { LayoutWrapper } from "./layout/LayoutWrapper"
import { Router } from "./routes";

const App = () => {
  return (
    (
      <AppProviders>
        <LayoutWrapper>
            <Router />
        </LayoutWrapper>
      </AppProviders>
    )
  );
};

export default App
