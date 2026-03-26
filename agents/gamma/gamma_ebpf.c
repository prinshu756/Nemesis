#include <linux/bpf.h>
#include <bpf/bpf_helpers.h>
#include <linux/ip.h>
#include <linux/if_ether.h>

//Blocked IP addresses

struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __type(key, __u32);   // IP
    __type(value, __u8);
    __uint(max_entries, 1024);
} blocked_ips SEC(".maps");

//Blocked MAC's addresses

struct mac_key {
    unsigned char mac[6];
};

struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __type(key, struct mac_key);
    __type(value, __u8);
    __uint(max_entries, 1024);
} blocked_macs SEC(".maps");

//XDP Program

SEC("xdp")
int xdp_filter(struct xdp_md *ctx) {

    void *data_end = (void *)(long)ctx->data_end;
    void *data = (void *)(long)ctx->data;

    struct ethhdr *eth = data;
    if ((void*)(eth + 1) > data_end)
        return XDP_PASS;

    //MAC Filtering
    struct mac_key src_mac = {};
    __builtin_memcpy(src_mac.mac, eth->h_source, 6);

    if (bpf_map_lookup_elem(&blocked_macs, &src_mac)) {
        return XDP_DROP;  // drop by MAC instantly
    }

  //IP Filtering
    if (eth->h_proto != __constant_htons(ETH_P_IP))
        return XDP_PASS;

    struct iphdr *ip = data + sizeof(*eth);
    if ((void*)(ip + 1) > data_end)
        return XDP_PASS;

    __u32 dst_ip = ip->daddr;

    if (bpf_map_lookup_elem(&blocked_ips, &dst_ip)) {
        return XDP_DROP;
    }

    return XDP_PASS;
}

char _license[] SEC("license") = "GPL";