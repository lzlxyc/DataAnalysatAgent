import argparse
from data_analyst_agent import create_agent

def main():
    parser = argparse.ArgumentParser(description="Data Analyst Agent")

    parser.add_argument("--model", type=str, default="deepseek-chat", help="")
    parser.add_argument("--env_path", type=str, default="./.env", help="环境文件路径")
    parser.add_argument("--is_enhanced_mode", default=False, help="是否开启增强模式")
    parser.add_argument("--is_developer_mode", default=False, help="当前对话是否开启开发者模式")

    args = parser.parse_args()

    agent = create_agent(
        model=args.model,
        env_path=args.env_path,
        is_enhanced_mode=args.is_enhanced_mode,
        is_developer_mode=args.is_developer_mode
    )
    agent.run()


if __name__ == "__main__":
    main()