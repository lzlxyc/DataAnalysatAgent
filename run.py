# from data_analyst_agent.main import main
from data_analyst_agent import create_agent


if __name__ == "__main__":
    agent = create_agent()
    agent.run()