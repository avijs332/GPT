import { AppProviders } from "./providers"
import { LayoutWrapper } from "./common/LayoutWrapper"
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
